import sys
import os
import pandas as pd
import certifi
import pymongo
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, Request
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Logging.Logger import logging
from Network_Security.Utils.main_utils.Main_Utils import load_object
from Network_Security.Pipelines.training_pipeline import TrainingPipeline
from Network_Security.Utils.ml_utils.model.estimator import NetworkModel
from Network_Security.Constants.Training_Pipeline import DATA_INGESTION_COLLECTION_NAME
from Network_Security.Constants.Training_Pipeline import DATA_INGESTION_DATABASE_NAME
ca = certifi.where()
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
client = pymongo.MongoClient(mongo_db_url,tlsCAFile = ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"])

from fastapi.templating import Jinja2Templates
templates = Jinja2Templates(directory = "./templates")

@app.get("/",tags = ["authentication"])
async def index():
    return RedirectResponse(url = "/docs")

@app.get("/train")
async def train_route():
    try: 
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return Response("Training is Successful")
    except Exception as e:
        raise NetworkSecurityException(e,sys)

@app.post("/predict")
async def predict_route(request : Request,file:UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)
        preprocessor = load_object("Final_Model/Preprocessor.pkl")
        final_model = load_object("Final_Model/Model.pkl")
        network_model = NetworkModel(preprocessor= preprocessor,model = final_model)
        print(df.iloc[0])
        y_pred = network_model.predict(df)
        print(y_pred)
        df['predicted_column'] = y_pred
        print(df["predicted_column"])
        df.to_csv("Prediction_Output/Output.csv")
        table_html = df.to_html(classes = "table table-striped")
        return templates.TemplateResponse('table.html',{'request': request,'table' : table_html})
    except Exception as e:
        raise NetworkSecurityException(e,sys)

if __name__ == "__main__":
    app_run(app,host = "localhost",port = 8000)