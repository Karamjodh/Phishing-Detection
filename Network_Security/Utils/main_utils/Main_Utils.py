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
