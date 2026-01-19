import os
import sys
import numpy as np
import pandas as pd
import pymongo
import certifi
from typing import List
from sklearn.model_selection import train_test_split
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Logging.Logger import logging
from Network_Security.Entity.config_entity import DataIngestionConfig
from Network_Security.Entity.artifact_entity import DataIngestionArtifact
from dotenv import load_dotenv

load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion :
    def __init__(self, data_ingestion_config : DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def export_collection_as_dataframe(self):
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name

            if not MONGO_DB_URL:
                raise ValueError("MONGO_DB_URL is missing. Check your .env and load_dotenv().")

            # Stronger, more reliable client
            self.mongo_client = pymongo.MongoClient(
                MONGO_DB_URL,
                tls=True,
                tlsCAFile=certifi.where(),
                serverSelectionTimeoutMS=30000,
                connectTimeoutMS=20000,
                socketTimeoutMS=20000,
            )

            # quick ping so errors show here clearly
            self.mongo_client.admin.command("ping")

            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)

            df.replace({"na": np.nan}, inplace=True)
            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def export_data_to_feature_store(self,dataframe : pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path,exist_ok = True)
            dataframe.to_csv(feature_store_file_path,index = False,header = True)
            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def split_data_as_train_test(self,dataframe : pd.DataFrame):
        try:
            train_set,test_set = train_test_split(dataframe,test_size = self.data_ingestion_config.train_test_split_ratio)
            logging.info("Performed train test split on the Dataframe")
            logging.info("Exited split_data_as_train_test method of Data_Ingestion Class")
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path,exist_ok = True)
            logging.info(f"Exporting train and test file path")
            train_set.to_csv(self.data_ingestion_config.training_file_path,index = False, header = True)
            test_set.to_csv(self.data_ingestion_config.testing_file_path,index = False, header = True)
            logging.info(f"Exported train and test file path")

        except Exception as e:
            raise NetworkSecurityException(e,sys)


    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_to_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            data_ingestion_artifact = DataIngestionArtifact(trained_file_path = self.data_ingestion_config.training_file_path,
                                                            test_file_path = self.data_ingestion_config.testing_file_path)
            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)
