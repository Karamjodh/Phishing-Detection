from Network_Security.Components.Data_Ingestion import DataIngestion
from Network_Security.Entity.config_entity import DataIngestionConfig
from Network_Security.Entity.config_entity import TrainingPipelineConfig
from Network_Security.Logging.Logger import logging
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Components.Data_Validation import DataValidation,DataValidationConfig
import sys

if __name__ == "__main__":
    try:
        trainingpipelineconfig = TrainingPipelineConfig()
        dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
        data_ingestion = DataIngestion(dataingestionconfig)
        logging.info("Initiating Data Ingestion")
        dataingestionartifact = data_ingestion.initiate_data_ingestion()
        logging.info("Data Ingestion Completed")
        print(dataingestionartifact)
        data_validation_config = DataValidationConfig(trainingpipelineconfig)
        data_validation = DataValidation(dataingestionartifact,data_validation_config)
        logging.info("Initiating Data Validation")
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data Validation Completed")
        print(data_validation_artifact)  

    except Exception as e:
        raise NetworkSecurityException(e,sys)