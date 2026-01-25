import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from Network_Security.Constants.Training_Pipeline import TARGET_COLUMN
from Network_Security.Constants.Training_Pipeline import DATA_TRANSFORMATION_TRANSFORMED_IMPUTER_PARAMS
from Network_Security.Entity.artifact_entity import (DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact)
from Network_Security.Entity.config_entity import DataTransformationConfig
from Network_Security.Logging.Logger import logging
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Utils.main_utils.Main_Utils import save_numpy_array_data,save_object

class DataTransformation:
    def __init__(self,data_validation_artifact : DataValidationArtifact,
                 data_transformation_config : DataTransformationConfig):
        try:
            self.data_validation_artifact : DataValidationArtifact = data_validation_artifact
            self.data_transformation_config : DataTransformationConfig = data_transformation_config

        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def get_data_transformer_object(cls) -> Pipeline:
        logging.info("Entered get_data_transformer_object in DataTransformation class")
        try:
            imputer = KNNImputer(**DATA_TRANSFORMATION_TRANSFORMED_IMPUTER_PARAMS)
            logging.info(f"Initalize KNNImputer with {DATA_TRANSFORMATION_TRANSFORMED_IMPUTER_PARAMS}")
            processor : Pipeline = Pipeline([("imputer",imputer)])
            return processor
        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def initiate_data_transformation(self)->DataTransformationArtifact:
        logging.info("Entered initiate_data_transformation mehtod of dataTransformation class")
        try:
            logging.info("Starting data tranformation")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            input_feature_train_df = train_df.drop(columns = [TARGET_COLUMN],axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1,0)

            input_feature_test_df = test_df.drop(columns = [TARGET_COLUMN],axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1,0)
            
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_feature_train_df)
            transformed_input_train_feature = preprocessor_object.transform(input_feature_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_feature_test_df)

            train_arr = np.c_[transformed_input_train_feature,np.array(target_feature_train_df)]
            test_arr = np.c_[transformed_input_test_feature,np.array(target_feature_test_df)]

            save_numpy_array_data(self.data_transformation_config.transformed_train_file_path,array = train_arr)
            save_numpy_array_data(self.data_transformation_config.transformed_test_file_path,array = test_arr)
            save_object(self.data_transformation_config.transformed_object_file_path,preprocessor_object,)

            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path = self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path = self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path = self.data_transformation_config.transformed_test_file_path
            )
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)