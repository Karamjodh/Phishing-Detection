import yaml
from Network_Security.Logging.Logger import logging
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
import os,sys
import numpy as np
# import dill
import pickle

def read_yaml_file(file_path : str) -> dict:
    try:
        with open(file_path,"rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        NetworkSecurityException(e,sys)
    
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if replace and os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as file:
            yaml.dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)
    
def save_numpy_array_data(file_path: str, array : np.array):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path,exist_ok = True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    
    except Exception as e:
        raise NetworkSecurityException(e,sys)
    
def save_object(file_path:str , obj : object) -> None:
    try:
        logging.info("Entered the Save Object method of Main Utils Class")
        os.makedirs(os.path.dirname(file_path),exist_ok = True)
        with open(file_path,"wb") as file_path:
            pickle.dump(obj,file_path)
        logging.info("Exited the save_bject method of main Utils class")
    except Exception as e:
        raise NetworkSecurityException(e,sys)


