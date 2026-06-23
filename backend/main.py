import certifi
import os
import shutil
import cv2
import base64
import numpy as np
import torch
import torchvision.transforms.functional as TF
import traceback

from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pydantic import BaseModel

IMAGE_SIZE = 512

class NewPatient(BaseModel):
    patient_id: str
    age: int
    sex: str

class AcceptedScan(BaseModel):
    file_name: str
    slice_index: int
    lesion_type: int
    ground_truth_box: list

# Pre-processing and prediction
def window_image(img, window_center=-600, window_width=1500):
    img = img.astype(np.float32)
    img = img - 32768.0          # convert to true HU
    low  = window_center - window_width / 2   # -1350
    high = window_center + window_width / 2   #   150
    img  = np.clip(img, low, high)
    img  = (img - low) / (high - low)         # [0, 1]
    return img
    
class LesionPredictor:
    def __init__(self, model_path, device='cpu', score_threshold=0.35):
        self.device = torch.device(device)
        self.threshold = score_threshold
        self.model = torch.jit.load(model_path, map_location=self.device)
        self.model.eval()
        self.model.to(self.device)

    def preprocess(self, png_path):
        base = os.path.basename(png_path)
        try:
            slice_idx = int(base.split('_')[-1].replace('.png', ''))
        except Exception:
            print(f"Warning: Filename '{base}' doesn't match DeepLesion format. Defaulting to slice index 0.")
            slice_idx = 0

        def read_slice(path):
            img = cv2.imread(path, cv2.IMREAD_ANYDEPTH)
            if img is None:
                return None
            img = img.astype(np.float32) - 32768.0
            low, high = -1350.0, 150.0
            img = np.clip(img, low, high)
            img = (img - low) / (high - low)
            return img

        center = read_slice(png_path)
        if center is None:
            raise FileNotFoundError(f"Cannot read {png_path}")

        prev_path = png_path.replace(f"{slice_idx:03d}.png", f"{max(slice_idx-1,0):03d}.png")
        next_path = png_path.replace(f"{slice_idx:03d}.png", f"{slice_idx+1:03d}.png")

        prev = read_slice(prev_path) if os.path.exists(prev_path) else center.copy()
        nxt  = read_slice(next_path) if os.path.exists(next_path) else center.copy()

        volume = np.stack([prev, center, nxt], axis=0)
        tensor = torch.from_numpy(volume)
        tensor = TF.resize(tensor, [IMAGE_SIZE, IMAGE_SIZE], antialias=True)
        print(f"DEBUG -> Tensor Min: {tensor.min().item()}, Max: {tensor.max().item()}")
        return tensor

    @torch.no_grad()
    def predict(self, png_path):
        tensor = self.preprocess(png_path).to(self.device)
        raw_output = self.model([tensor])
        preds = raw_output[1][0]

        keep = preds['scores'] >= self.threshold
        boxes = preds['boxes'][keep].cpu().tolist()
        scores = preds['scores'][keep].cpu().tolist()

        return [
            {'box': box, 'score': round(score, 4)}
            for box, score in zip(boxes, scores)
        ]

# FASTAPI setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading PyTorch model...")
predictor = LesionPredictor(model_path='model_scripted.pt', device='cpu', score_threshold=0.35)

# Connect to MongoDB
uri = "mongodb+srv://steopannicola26_db_user:WV1O6OZ4u5umqwKp@cluster0.dszi3ca.mongodb.net/?appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
db = client["ct_application"]
patients_collection = db["patients"]


STORAGE_DIR = os.path.join("static", "ct_scans")
os.makedirs(STORAGE_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# API ENDPOINTS 

# GET
@app.get("/api/patients/{patient_id}")
def get_patient(patient_id: str):
    padded_id = patient_id.zfill(6)
    patient = patients_collection.find_one({"patient_id": padded_id}, {"_id": 0})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.get("/api/view-scan/{file_name:path}")
def view_windowed_scan(file_name: str, raw: bool = False): 
    """
    Smart image proxy: Locates raw files across multiple historical directories.
    Can serve raw images or windowed images based on query parameters.
    """
    clean_name = os.path.basename(file_name)
    
    POSSIBLE_RAW_DIRS = [
        "static/ct_scans",
        "static/ct_scans/images_png"
    ]
    
    CACHE_DIR = "static/ct_scans"
    processed_filename = f"windowed_{clean_name}"
    processed_path = os.path.abspath(os.path.join(CACHE_DIR, processed_filename))

    raw_path = None
    for directory in POSSIBLE_RAW_DIRS:
        test_path = os.path.abspath(os.path.join(directory, clean_name))
        if os.path.exists(test_path):
            raw_path = test_path
            break

    if not raw_path:
        raise HTTPException(status_code=404, detail=f"File '{clean_name}' not found.")

    if raw:
        return FileResponse(raw_path, media_type="image/png")

    if os.path.exists(processed_path):
        return FileResponse(processed_path, media_type="image/png")

    try:
        raw_img = cv2.imread(raw_path, cv2.IMREAD_ANYDEPTH)
        if raw_img is not None:
            windowed = window_image(raw_img)
            windowed_8bit = (windowed * 255).astype(np.uint8)
            os.makedirs(CACHE_DIR, exist_ok=True)
            cv2.imwrite(processed_path, windowed_8bit)
            return FileResponse(processed_path, media_type="image/png")
    except Exception as e:
        print(f"On-the-fly windowing failed for {clean_name}: {e}")
        
    return FileResponse(raw_path, media_type="image/png")



# POST

@app.post("/api/patients")
def add_patient(patient: NewPatient):
    padded_id = patient.patient_id.zfill(6)
    existing = patients_collection.find_one({"patient_id": padded_id})
    if existing:
        raise HTTPException(status_code=400, detail="Patient ID already exists")
    new_doc = {"patient_id": padded_id, "age": patient.age, "sex": patient.sex, "studies": []}
    patients_collection.insert_one(new_doc)
    return {"status": "success"}


@app.post("/api/predict")
def predict_abnormality(main_slice: UploadFile = File(...)):
    if not main_slice.filename.endswith('.png'):
        raise HTTPException(400, "Only PNG files accepted")

    file_path = os.path.join(STORAGE_DIR, main_slice.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(main_slice.file, buffer)

    try:
        # Run AI model
        results = predictor.predict(file_path)
        
        processed_filename = f"windowed_{main_slice.filename}"
        processed_file_path = os.path.join(STORAGE_DIR, processed_filename)
        
        raw_img = cv2.imread(file_path, cv2.IMREAD_ANYDEPTH)
        if raw_img is not None:
            windowed = window_image(raw_img)
            windowed_8bit = (windowed * 255).astype(np.uint8)
            cv2.imwrite(processed_file_path, windowed_8bit)
            processed_image_url = f"http://localhost:8000/static/ct_scans/{processed_filename}"
        else:
            processed_image_url = f"http://localhost:8000/static/ct_scans/{main_slice.filename}"

        vue_findings = [
            {"type": "Lung Lesion", "probability": round(res['score'] * 100, 1), "bbox": res['box']}
            for res in results
        ]

        return {
            "status": "success",
            "findings": vue_findings,
            "processed_image": processed_image_url
        }

    except Exception as e:
        print("--- AI PREDICTION CRASHED ---")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/patients/{patient_id}/add_scan")
def save_accepted_scan(patient_id: str, scan: AcceptedScan):
    padded_id = patient_id.zfill(6)
    
    patient = patients_collection.find_one({"patient_id": padded_id})
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    study_exists = any(s.get("study_index") == 1 for s in patient.get("studies", []))
    if not study_exists:
        patients_collection.update_one(
            {"patient_id": padded_id},
            {"$push": {"studies": {"study_index": 1, "scans": []}}}
        )
    
    new_scan_doc = {
        "file_name": scan.file_name,
        "slice_index": scan.slice_index,
        "lesion_type": scan.lesion_type,
        "ground_truth_box": scan.ground_truth_box,
        "image_url": f"http://localhost:8000/static/ct_scans/{scan.file_name}",
        "processed_image_url": f"http://localhost:8000/static/ct_scans/windowed_{scan.file_name}"
    }

    patients_collection.update_one(
        {"patient_id": padded_id, "studies.study_index": 1},
        {"$push": {"studies.$.scans": new_scan_doc}}
    )
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)