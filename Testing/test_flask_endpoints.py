"""
Test script to debug Flask endpoint
Run this to test if the /predict-url endpoint is working
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=" * 80)
    print("Testing /health endpoint...")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Health check passed!")
            print(f"   Model loaded: {data.get('model_loaded')}")
            print(f"   Database connected: {data.get('database_connected')}")
        else:
            print(f"\n❌ Health check failed!")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print()


def test_predict_url(url):
    """Test predict-url endpoint"""
    print("=" * 80)
    print(f"Testing /predict-url endpoint with: {url}")
    print("=" * 80)
    
    try:
        payload = {"url": url}
        headers = {'Content-Type': 'application/json'}
        
        print(f"Sending POST request to: {BASE_URL}/predict-url")
        print(f"Payload: {json.dumps(payload)}")
        print(f"Headers: {headers}")
        print()
        
        response = requests.post(
            f"{BASE_URL}/predict-url",
            json=payload,
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('Content-Type')}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        print(f"Response Text (first 500 chars):")
        print(response.text[:500])
        print()
        
        # Try to parse as JSON
        try:
            data = response.json()
            print("✅ Valid JSON response!")
            print(f"Prediction: {data.get('prediction')}")
            print(f"Confidence: {data.get('confidence')}")
            print(f"URL: {data.get('url')}")
            if 'error' in data:
                print(f"Error: {data.get('error')}")
                print(f"Message: {data.get('message')}")
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON! JSONDecodeError: {str(e)}")
            print(f"   Response is likely HTML error page")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    
    print()


def check_server():
    """Check if server is running"""
    print("=" * 80)
    print("Checking if Flask server is running...")
    print("=" * 80)
    
    try:
        response = requests.get(BASE_URL, timeout=2)
        print(f"✅ Server is running at {BASE_URL}")
        print(f"   Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is NOT running at {BASE_URL}")
        print("   Please start the Flask app first:")
        print("   python App_Flask.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    print()
    return True


if __name__ == "__main__":
    print("\n🔍 FLASK ENDPOINT DEBUGGING TOOL\n")
    
    # Check if server is running
    if not check_server():
        exit(1)
    
    # Test health endpoint
    test_health()
    
    # Test predict-url endpoint
    test_urls = [
        "https://www.google.com",
        "http://bit.ly/test",
        "https://github.com"
    ]
    
    for url in test_urls:
        test_predict_url(url)
        print("\n" + "=" * 80 + "\n")
    
    print("✅ Testing complete!")
    print("\nIf you see 'Invalid JSON' errors, the server is returning HTML instead of JSON.")
    print("Common causes:")
    print("1. url_feature_extractor.py is missing or not found")
    print("2. Python exception in the endpoint")
    print("3. FEATURE_ORDER doesn't match your model")
    print("4. Models not loaded (check console when starting Flask app)")