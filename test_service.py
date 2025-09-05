#!/usr/bin/env python3
"""
Test script for the MusicGen Modal service.
This script tests local deployment and basic functionality.
"""

import json
import base64
import os
from pathlib import Path

def test_local_generation():
    """Test music generation locally using Modal's local testing."""
    try:
        from modal_service import app
        
        print("🎵 Testing MusicGen service locally...")
        
        # Test data
        test_request = {
            "prompt": "upbeat electronic dance music",
            "duration": 5.0,  # Short duration for testing
            "temperature": 1.0,
            "cfg_coef": 3.0,
            "model_size": "small"
        }
        
        print(f"Request: {json.dumps(test_request, indent=2)}")
        
        # Call the generate function
        with app.run():
            result = app.lookup("generate").remote(test_request)
            
        print(f"Response received: {result.get('success', False)}")
        
        if result.get("success"):
            # Decode and save audio for testing
            audio_data = result.get("audio_data")
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                
                # Save to test file
                test_output = Path("test_output.wav")
                test_output.write_bytes(audio_bytes)
                
                print(f"✅ Generated audio saved to: {test_output}")
                print(f"   File size: {len(audio_bytes)} bytes")
                print(f"   Duration: {result.get('duration')} seconds")
                
                return True
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Local test failed: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        from modal_service import app
        
        print("🏥 Testing health endpoint...")
        
        with app.run():
            result = app.lookup("health").remote()
            
        print(f"Health check result: {result}")
        return result.get("status") == "healthy"
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_list_models():
    """Test the list models endpoint."""
    try:
        from modal_service import app
        
        print("📋 Testing list models endpoint...")
        
        with app.run():
            result = app.lookup("list_models").remote()
            
        print(f"Available models: {json.dumps(result, indent=2)}")
        return "models" in result
        
    except Exception as e:
        print(f"❌ List models failed: {e}")
        return False

def validate_environment():
    """Validate the environment setup."""
    print("🔍 Validating environment...")
    
    try:
        import modal
        print(f"✅ Modal version: {modal.__version__}")
    except ImportError:
        print("❌ Modal not installed")
        return False
    
    # Check Modal token
    try:
        from modal import App
        test_app = App("test")
        print("✅ Modal authentication OK")
    except Exception as e:
        print(f"❌ Modal authentication failed: {e}")
        print("   Please run: modal token new")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting MusicGen Modal Service Tests\n")
    
    # Validate environment
    if not validate_environment():
        print("\n❌ Environment validation failed!")
        return False
    
    print()
    
    # Test endpoints
    tests = [
        ("Health Check", test_health_endpoint),
        ("List Models", test_list_models),
        ("Music Generation", test_local_generation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed! Service is ready to deploy.")
        print("\nNext steps:")
        print("1. Deploy to Modal: modal deploy modal_service.py")
        print("2. Get the endpoint URL and update your environment variables")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed. Please fix issues before deploying.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
