import os
import sys
import json 
import certifi 
import pymongo
import pandas as pd
import numpy as np
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Logging.Logger import logging
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print(MONGO_DB_URL)

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def csv_to_json_convertor(self,file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop = True,inplace = True)
            records = list(json.loads(data.T.to_json()).values()) 
            ## Here to_json create a json object which is key-valued pair of the data but by default it does that by taking columns as primary key 
            ## i.e {column1 : {"0" : "df[0,0]_value", "1" : "df[1,0]" , ...} , column1 : {"0" : "df[0,0]_value", "1" : "df[1,0]" , ...}} but we dont 
            ## want that we want the data jsoned wrt to each row and therefore either we can transpose the data or we can put argument (orient = "records") 
            ## this will give us {0 : {"column1" : "df[0,0]_value", "column2" : "df[0,1]" , ...} , 1 : {"column1" : "df[0,0]_value", "column2" : "df[0,1]" , ...}}
            ## [{"column1" : "df[0,0]_value", "column2" : "df[0,1]" , ...} , 1 : {"column1" : "df[0,0]_value", "column2" : "df[0,1]" , ...}] respectively 
            ## and thus we can also use json.loads(data.T.to_json(orient = "records")) and there will be no use of .T to transpose and .values() to access 
            ## values in the nested dictionary
            return records
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def insert_data_to_mongodb(self,records,database,collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]

            self.collection.insert_many(self.records)
            return(len(self.records))
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
if __name__ == "__main__":
    FILE_PATH = "Network_Data\phisingData.csv"
    DATABASE = "karamjodh_db_user"
    Collection = "NetworkData"
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json_convertor(file_path = FILE_PATH)
    print(records)
    no_of_records = networkobj.insert_data_to_mongodb(records,DATABASE,Collection)
    print(no_of_records)