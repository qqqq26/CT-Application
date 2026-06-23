# CT-Application


From the DeepLesion dataset(https://nihcc.app.box.com/v/DeepLesion/folder/51877983116), we filtered only the CT scans containing the lungs. The dataset can be found here: https://drive.google.com/drive/folders/1aJDrGmXKK_pvTfYXFq0PL2G15NOTn1YK?usp=sharing. 


###Dependencies: 
**Python**: version 3.10 or higher
**Node.js**: version 18.0 or higher
**MongoDB**

###Structure:
|--- backend/ 
|       |--- main.py
|       |--- static/ #Contains the data, but it is too big to upload here
|       |--- requirements.txt
|--- frontend/
        |--- src/ # Components, Views, Router
        |--- package.json
        |--- vite.config.js


####Run backend
cd backend
pip install -r requirements.txt
python main.py


####Run frontend
cd frontend
npm install
npm run dev

