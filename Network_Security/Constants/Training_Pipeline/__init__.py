import os

"""
defining common constant variables
"""
TARGET_COLUMN = "Result"
PIPELINE_NAME = "NetworkSecurity"
ARTIFACT_DIR = "Artifacts"
FILE_NAME = "phishingData.csv"
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"

"""
Data Ingestion related constant 
"""
DATA_INGESTION_COLLECTION_NAME : str = "NetworkData"
DATA_INGESTION_DATABASE_NAME : str = "karamjodh_db_user"
DATA_INGESTION_DIR_NAME : str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR : str = "feature_store"
DATA_INGESTION_INGESTED_DIR : str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO : float = 0.2



#                                         --------feature_store/phishingData.csv
#                                        |
#                                        |
# Artifacts/TimeStamp/data_ingestion------                       --------train.csv
#                                        |                      |
#                                        |                      |
#                                         ---------ingested------
#                                                               |
#                                                               |
#                                                                --------test.csv

"""
Data Validation related constants 
"""

DATA_VALIDATION_DIR_NAME : str = "data_validation"
DATA_VALIDATION_VALID_DIR : str = "validated"
DATA_VALIDATION_INVALID_DIR : str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR : str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME : str = "report.yaml"
SCHEMA_FILE_PATH = os.path.join("data_schema","schema.yaml")