"""
Test script for SageMaker endpoint
Run this after deployment to verify the endpoint works
"""

import boto3
import json

def test_endpoint(endpoint_name='iris-classifier-endpoint'):
    """Test the deployed SageMaker endpoint"""
    
    runtime = boto3.client('sagemaker-runtime')
    
    # Test data - sample iris measurements
    test_data = {
        "instances": [
            [5.1, 3.5, 1.4, 0.2],  # Should predict class 0 (setosa)
            [6.2, 2.9, 4.3, 1.3],  # Should predict class 1 (versicolor)
            [7.3, 2.9, 6.3, 1.8]   # Should predict class 2 (virginica)
        ]
    }
    
    print(f"Testing endpoint: {endpoint_name}")
    print(f"Input data: {test_data}")
    
    try:
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(test_data)
        )
        
        result = json.loads(response['Body'].read().decode())
        
        print("\n✓ Endpoint is working!")
        print(f"\nPredictions: {result['predictions']}")
        print(f"\nProbabilities:")
        for i, probs in enumerate(result['probabilities']):
            print(f"  Sample {i+1}: {[f'{p:.4f}' for p in probs]}")
        
        return result
        
    except Exception as e:
        print(f"\n✗ Error testing endpoint: {str(e)}")
        raise

if __name__ == "__main__":
    import sys
    
    endpoint_name = sys.argv[1] if len(sys.argv) > 1 else 'iris-classifier-endpoint'
    test_endpoint(endpoint_name)
