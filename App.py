import sys
import os
import pandas as pd
import certifi
import pymongo
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS

from Network_Security.Exception_Handling.Exception import NetworkSecurityException
from Network_Security.Logging.Logger import logging
from Network_Security.Utils.main_utils.Main_Utils import load_object
from Network_Security.Pipelines.training_pipeline import TrainingPipeline
from Network_Security.Utils.ml_utils.model.estimator import NetworkModel
from Network_Security.Constants.Training_Pipeline import DATA_INGESTION_COLLECTION_NAME
from Network_Security.Constants.Training_Pipeline import DATA_INGESTION_DATABASE_NAME
from Network_Security.Utils.extractor.url_feature_extractor import URLFeatureExtractor

# MongoDB setup
ca = certifi.where()
load_dotenv()
mongo_db_url = os.getenv("MONGODB_URL_KEY")
print(mongo_db_url)
client = pymongo.MongoClient(mongo_db_url, tlsCAFile=ca)
database = client[DATA_INGESTION_DATABASE_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

# Flask app
app = Flask(__name__,template_folder='Templates')
CORS(app)

# Global error handler to return JSON instead of HTML
@app.errorhandler(Exception)
def handle_error(e):
    """Global error handler to return JSON for all errors"""
    logging.error(f"Unhandled error: {str(e)}", exc_info=True)
    
    # If it's a NetworkSecurityException, handle it
    if isinstance(e, NetworkSecurityException):
        return jsonify({
            'error': 'Application Error',
            'message': str(e)
        }), 500
    
    # For all other exceptions
    return jsonify({
        'error': 'Internal Server Error',
        'message': str(e)
    }), 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle 405 errors"""
    return jsonify({
        'error': 'Method Not Allowed',
        'message': 'The method is not allowed for this endpoint'
    }), 405

# Load models at startup
preprocessor = None
final_model = None
network_model = None

try:
    preprocessor = load_object("Final_Model/Preprocessor.pkl")
    final_model = load_object("Final_Model/Model.pkl")
    network_model = NetworkModel(preprocessor=preprocessor, model=final_model)
    logging.info("Models loaded successfully for real-time prediction")
except Exception as e:
    logging.warning(f"Could not load models at startup: {e}")

# CRITICAL: Replace this with your actual feature order from data_schema/schema_training.json
FEATURE_ORDER = [
    'having_IP_Address', 'URL_Length', 'Shortining_Service', 'having_At_Symbol',
    'double_slash_redirecting', 'Prefix_Suffix', 'having_Sub_Domain', 'SSLfinal_State',
    'Domain_registeration_length', 'Favicon', 'port', 'HTTPS_token', 'Request_URL',
    'URL_of_Anchor', 'Links_in_tags', 'SFH', 'Submitting_to_email', 'Abnormal_URL',
    'Redirect', 'on_mouseover', 'RightClick', 'popUpWidnow', 'Iframe', 'age_of_domain',
    'DNSRecord', 'web_traffic', 'Page_Rank', 'Google_Index', 'Links_pointing_to_page',
    'Statistical_report'
]


@app.route('/')
def index():
    """Home page with URL input form"""
    return render_template('index.html')


@app.route('/train')
def train_route():
    """Train the model pipeline"""
    try:
        train_pipeline = TrainingPipeline()
        train_pipeline.run_pipeline()
        return jsonify({"message": "Training is Successful"})
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.route('/predict', methods=['POST'])
def predict_route():
    """Original CSV file upload prediction endpoint"""
    try:
        file = request.files['file']
        df = pd.read_csv(file)
        
        # Load models if not already loaded
        if network_model is None:
            preprocessor_obj = load_object("Final_Model/Preprocessor.pkl")
            model_obj = load_object("Final_Model/Model.pkl")
            network_model_temp = NetworkModel(preprocessor=preprocessor_obj, model=model_obj)
        else:
            network_model_temp = network_model
        
        print(df.iloc[0])
        y_pred = network_model_temp.predict(df)
        print(y_pred)
        
        df['predicted_column'] = y_pred
        print(df["predicted_column"])
        
        df.to_csv("Prediction_Output/Output.csv")
        table_html = df.to_html(classes="table table-striped")
        
        return render_template('table.html', table=table_html)
    
    except Exception as e:
        raise NetworkSecurityException(e, sys)


@app.route('/predict-url', methods=['POST'])
def predict_url():
    """NEW: Real-time single URL prediction endpoint"""
    try:
        # Get JSON data
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL cannot be empty'}), 400
        
        # Check if models are loaded
        if network_model is None:
            return jsonify({'error': 'Model not loaded. Please train the model first.'}), 500
        
        logging.info(f"Processing URL: {url}")
        
        # Extract features from URL
        extractor = URLFeatureExtractor(url, timeout=10)
        features = extractor.extract_all_features()
        
        logging.info(f"Extracted {len(features)} features")
        
        # Convert features to DataFrame with correct order
        feature_df = pd.DataFrame([features])
        feature_df = feature_df[FEATURE_ORDER]
        
        # Make prediction
        prediction = network_model.predict(feature_df)
        
        # Get prediction label (adjust based on your model's output)
        if prediction[0] == -1 :
            result_label = 'Phishing'
        elif prediction[0] == 1:
            result_label = 'Safe'
        else:
            result_label = 'Suspicious'
        
        # Try to get confidence
        confidence = None
        try:
            if hasattr(network_model.model, 'predict_proba'):
                proba = network_model.model.predict_proba(
                    network_model.preprocessor.transform(feature_df)
                )[0]
                confidence = float(max(proba)) * 100
        except Exception as e:
            logging.warning(f"Could not get probability: {e}")
        
        logging.info(f"Prediction: {result_label} (Confidence: {confidence}%)")
        
        response = jsonify({
            'url': url,
            'prediction': result_label,
            'confidence': confidence,
            'features': features
        })
        response.headers['Content-Type'] = 'application/json'
        return response
    
    except Exception as e:
        logging.error(f"Error during URL prediction: {str(e)}", exc_info=True)
        response = jsonify({
            'error': 'Prediction failed',
            'message': str(e)
        })
        response.headers['Content-Type'] = 'application/json'
        return response, 500


@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    """NEW: Batch URL prediction endpoint"""
    try:
        data = request.get_json()
        urls = data.get('urls', [])
        
        if not urls or not isinstance(urls, list):
            return jsonify({'error': 'Invalid input. Provide a list of URLs'}), 400
        
        if network_model is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        results = []
        
        for url in urls:
            try:
                # Extract features
                extractor = URLFeatureExtractor(url, timeout=5)
                features = extractor.extract_all_features()
                
                # Convert to DataFrame
                feature_df = pd.DataFrame([features])
                feature_df = feature_df[FEATURE_ORDER]
                
                # Predict
                prediction = network_model.predict(feature_df)
                result_label = 'Phishing' if prediction[0] == -1 or prediction[0] == 1 else 'Safe'
                
                # Get confidence
                confidence = None
                try:
                    if hasattr(network_model.model, 'predict_proba'):
                        proba = network_model.model.predict_proba(
                            network_model.preprocessor.transform(feature_df)
                        )[0]
                        confidence = float(max(proba)) * 100
                except:
                    pass
                
                results.append({
                    'url': url,
                    'prediction': result_label,
                    'confidence': confidence
                })
            
            except Exception as e:
                results.append({
                    'url': url,
                    'error': str(e)
                })
        
        return jsonify({
            'results': results,
            'total': len(urls)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': network_model is not None,
        'database_connected': client is not None,
        'features_count': len(FEATURE_ORDER)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)