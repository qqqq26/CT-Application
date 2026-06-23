# CT-Application


From the DeepLesion dataset(https://nihcc.app.box.com/v/DeepLesion/folder/51877983116), we filtered only the CT scans containing the lungs. The dataset can be found here: https://drive.google.com/drive/folders/1aJDrGmXKK_pvTfYXFq0PL2G15NOTn1YK?usp=sharing. 



### Dependencies: 
**Python**: version 3.10 or higher <br>
**Node.js**: version 18.0 or higher <br>
**MongoDB** <br>

### Structure:
|--- backend/ <br>
|       |--- main.py <br>
|       |--- static/ #Contains the data, but it is too big to upload here <br>
|       |--- requirements.txt <br>
|--- frontend/ <br> 
        |--- src/ # Components, Views, Router <br>
        |--- package.json <br>
        |--- vite.config.js <br>


### Run backend
cd backend <br>
pip install -r requirements.txt <br>
python main.py <br>


### Run frontend
cd frontend <br>
npm install <br> 
npm run dev <br>

