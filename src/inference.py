"""
Inference Script for SageMaker Endpoint
Handles model loading and prediction requests
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

def model_fn(model_dir):
    """
    Load the model for inference
    Called once when the endpoint starts
    """
    print(f"Loading model from {model_dir}")
    model_path = os.path.join(model_dir, "model.pkl")
    model = joblib.load(model_path)
    print("Model loaded successfully")
    return model

def input_fn(request_body, request_content_type):
    """
    Deserialize and prepare the prediction input
    """
    print(f"Received content type: {request_content_type}")
    
    if request_content_type == "application/json":
        data = json.loads(request_body)
        
        # Handle both single prediction and batch predictions
        if isinstance(data, dict):
            if "instances" in data:
                # Batch format: {"instances": [[...], [...]]}
                input_data = pd.DataFrame(data["instances"])
            elif "data" in data:
                # Alternative format: {"data": [[...], [...]]}
                input_data = pd.DataFrame(data["data"])
            else:
                # Single instance as dict: {"feature1": value1, ...}
                input_data = pd.DataFrame([data])
        elif isinstance(data, list):
            # Direct list format: [[...], [...]]
            input_data = pd.DataFrame(data)
        else:
            raise ValueError(f"Unsupported input format: {type(data)}")
        
        print(f"Input shape: {input_data.shape}")
        return input_data
    
    elif request_content_type == "text/csv":
        # Handle CSV input
        from io import StringIO
        input_data = pd.read_csv(StringIO(request_body), header=None)
        return input_data
    
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Make predictions using the loaded model
    """
    print(f"Making predictions for {len(input_data)} samples")
    predictions = model.predict(input_data)
    probabilities = model.predict_proba(input_data)
    
    return {
        "predictions": predictions.tolist(),
        "probabilities": probabilities.tolist()
    }

def output_fn(prediction, response_content_type):
    """
    Serialize the prediction output
    """
    if response_content_type == "application/json":
        return json.dumps(prediction), response_content_type
    
    raise ValueError(f"Unsupported response content type: {response_content_type}")
