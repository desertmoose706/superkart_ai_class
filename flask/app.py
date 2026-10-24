import hmac
import os
from flask import Flask, request, jsonify
import joblib
import pandas as pd

# Initialize the Flask application
superkart_api = Flask(__name__)

# API key is supplied at runtime through the environment (never hard-coded)
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set")

# Load the serialized machine learning model
model = joblib.load('superkart_model.joblib')


@superkart_api.before_request
def require_api_key():
    # Reject any request that does not carry the correct X-API-Key header
    provided = request.headers.get('X-API-Key', '')
    if not hmac.compare_digest(provided.encode(), API_KEY.encode()):
        return jsonify({"error": "Unauthorized"}), 401

def missing_columns(df):
    # Columns the trained pipeline needs that the request did not provide
    return [c for c in model.feature_names_in_ if c not in df.columns]


@superkart_api.route('/v1/predict', methods=['POST'])
def predict():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Convert the JSON payload into a pandas DataFrame
    df = pd.DataFrame([data])

    missing = missing_columns(df)
    if missing:
        return jsonify({"error": "Missing columns", "missing": missing}), 400
    
    # Generate a prediction
    prediction = model.predict(df)
    
    # Return the prediction as a JSON response
    return jsonify({"predicted_sales": float(prediction[0])})

@superkart_api.route('/v1/predictbatch', methods=['POST'])
def predictbatch():
    # Check if a file was uploaded in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    
    # Read the uploaded CSV file into a pandas DataFrame
    df = pd.read_csv(file)

    missing = missing_columns(df)
    if missing:
        return jsonify({"error": "Missing columns", "missing": missing}), 400
    
    # Generate predictions for the entire batch
    predictions = model.predict(df)
    
    # Convert predictions to a dictionary where keys are row indices
    predictions_dict = {str(i): float(pred) for i, pred in enumerate(predictions)}
    
    # Return the dictionary of predictions as a JSON response
    return jsonify(predictions_dict)

if __name__ == '__main__':
    # Run the Flask app on host 0.0.0.0 and port 7860
    superkart_api.run(host='0.0.0.0', port=7860)
