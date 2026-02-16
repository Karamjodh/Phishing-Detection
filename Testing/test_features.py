"""
Test script to verify the feature extraction pipeline
"""

from Network_Security.Utils.extractor.url_feature_extractor import URLFeatureExtractor
import json

def test_feature_extraction():
    """Test feature extraction with sample URLs"""
    
    test_urls = [
        "https://www.google.com",
        "https://www.github.com",
        "http://192.168.1.1",
        "http://bit.ly/test123",
        "https://secure-login-paypal.com",
    ]
    
    print("=" * 80)
    print("TESTING FEATURE EXTRACTION PIPELINE")
    print("=" * 80)
    
    for idx, url in enumerate(test_urls, 1):
        print(f"\n{idx}. Testing URL: {url}")
        print("-" * 80)
        
        try:
            extractor = URLFeatureExtractor(url, timeout=5)
            features = extractor.extract_all_features()
            
            print(f"✅ Successfully extracted {len(features)} features\n")
            
            # Display features
            feature_summary = {
                'Safe Features (1)': 0,
                'Suspicious Features (0)': 0,
                'Risky Features (-1)': 0
            }
            
            for feature_name, value in features.items():
                if value == 1:
                    feature_summary['Safe Features (1)'] += 1
                elif value == 0:
                    feature_summary['Suspicious Features (0)'] += 1
                else:
                    feature_summary['Risky Features (-1)'] += 1
            
            print("Feature Summary:")
            for category, count in feature_summary.items():
                print(f"  {category}: {count}")
            
            # Show first 5 features as example
            print("\nSample Features:")
            for i, (name, value) in enumerate(list(features.items())[:5], 1):
                status = "✅" if value == 1 else "⚠️" if value == 0 else "❌"
                print(f"  {i}. {name}: {value} {status}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


def test_api_format():
    """Test that features are in correct format for API"""
    
    print("\n" + "=" * 80)
    print("TESTING API FORMAT")
    print("=" * 80)
    
    url = "https://www.google.com"
    extractor = URLFeatureExtractor(url, timeout=5)
    features = extractor.extract_all_features()
    
    # Convert to JSON to test serialization
    api_response = {
        'url': url,
        'features': features,
        'feature_count': len(features)
    }
    
    try:
        json_str = json.dumps(api_response, indent=2)
        print("\n✅ API Response Format (Valid JSON):\n")
        print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
        print(f"\n✅ All {len(features)} features are JSON serializable")
    except Exception as e:
        print(f"\n❌ JSON Serialization Error: {str(e)}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    print("\n🔍 PHISHING URL DETECTION - FEATURE EXTRACTION TEST\n")
    
    # Test 1: Feature Extraction
    test_feature_extraction()
    
    # Test 2: API Format
    test_api_format()
    
    print("\n✅ All tests completed!")
    print("\nNext steps:")
    print("1. Verify your model is at: Final_Model/model.pkl")
    print("2. Update FEATURE_ORDER in app.py to match your training order")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:5000\n")

# Force run -> python -m Testing.test_features