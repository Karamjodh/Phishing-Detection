import os
import sys
import mlflow
from Network_Security.Logging.Logger import logging
from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Entity.artifact_entity import DataTransformationArtifact,ModelTrainerArtifact
from Network_Security.Entity.config_entity import ModelTrainerConfig
from Network_Security.Utils.ml_utils.model.estimator import NetworkModel
from Network_Security.Utils.main_utils.Main_Utils import save_object,load_object
from Network_Security.Utils.main_utils.Main_Utils import load_numpy_array_data,evaluate_models
from Network_Security.Utils.ml_utils.metric.classification_metric import get_classification_score
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (AdaBoostClassifier,GradientBoostingClassifier,RandomForestClassifier)
import dagshub

dagshub_token = os.getenv('DAGSHUB_USER_TOKEN')
if dagshub_token:
    os.environ['DAGSHUB_USER_TOKEN'] = dagshub_token
dagshub.init(repo_owner='Karamjodh', repo_name='Network-Security', mlflow=True)

class ModelTrainer:
    def __init__(self,model_trainer_config : ModelTrainerConfig,data_transformation_artifact : DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def track_mlflow(self,best_model,classificationmetric):
        with mlflow.start_run():
            f1_score = classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score = classificationmetric.recall_score
            mlflow.log_metric("f1_score",f1_score)
            mlflow.log_metric("precision_score",precision_score)
            mlflow.log_metric("recall_score",recall_score)
            mlflow.sklearn.log_model(best_model,"model")
        
    def train_model(self,X_train,Y_train,X_test,Y_test):
        models = {
            "Random Forest" : RandomForestClassifier(),
            "Decision Tree" : DecisionTreeClassifier(),
            "Gradient Boosting" : GradientBoostingClassifier(),
            "Logistic Regression" : LogisticRegression(),
            "AdaBoost" : AdaBoostClassifier()
        }
        params = {
            "Decision Tree" : {
                "criterion" : ['gini', 'entropy','log_loss'],
            },
            "Random Forest" : {
                "n_estimators" : [8,16,32,64,128,256],
            },
            "Gradient Boosting" : {
                "learning_rate" : [0.1,0.01,0.05,0.001],
                "subsample" : [0.6,0.7,0.75,0.8,0.85,0.9],
            },
            "Logistic Regression" : {},
            "AdaBoost" : {
                "learning_rate" : [0.1,0.01,0.05,0.001],
                "n_estimators" : [8,16,32,64,128,256],
            }
        }
        model_report : dict = evaluate_models(X_train = X_train,Y_train = Y_train,X_test = X_test,Y_test = Y_test,models = models,params = params)
        best_model_name = max(model_report, key=model_report.get)
        best_model_score = model_report[best_model_name]
        best_model = models[best_model_name]
        best_model.fit(X_train, Y_train)
        Y_train_pred = best_model.predict(X_train)
        classificaton_train_metric = get_classification_score(Y_train,Y_train_pred)
        self.track_mlflow(best_model,classificaton_train_metric)
        Y_test_pred = best_model.predict(X_test)
        classificaton_test_metric = get_classification_score(Y_test,Y_test_pred)
        self.track_mlflow(best_model,classificaton_test_metric)
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok = True)
        Network_Model = NetworkModel(preprocessor = preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj = Network_Model)
        save_object("Final_Model/Model.pkl",best_model)
        model_trainer_artifact = ModelTrainerArtifact(trained_model_file_path = self.model_trainer_config.trained_model_file_path,train_metric_artifact = classificaton_train_metric,test_metric_artifact = classificaton_test_metric)
        logging.info(f"Model trainer artifact : {model_trainer_artifact}")
        return model_trainer_artifact
  
    def initiate_model_trainer(self) ->ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            X_train,Y_train,X_test,Y_test = (
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )
            model = self.train_model(X_train,Y_train,X_test,Y_test)

        except Exception as e:
            raise NetworkSecurityException(e,sys)
        