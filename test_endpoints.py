#!/usr/bin/env python3
"""
Test the deployed Modal service endpoints.
"""

import requests
import json
import base64
from pathlib import Path
import time

# Modal endpoint URLs (update these with your actual URLs)
ENDPOINTS = {
    "health": "https://tranthai0414--musicgen-service-health.modal.run",
    "list_models": "https://tranthai0414--musicgen-service-list-models.modal.run", 
    "generate": "https://tranthai0414--musicgen-service-generate.modal.run"
}

def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(ENDPOINTS["health"], timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health check passed: {data}")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_list_models():
    """Test the list models endpoint."""
    print("📋 Testing list models endpoint...")
    try:
        response = requests.get(ENDPOINTS["list_models"], timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Models list received:")
        for model in data.get("models", []):
            print(f"   - {model['name']}: {model['description']}")
        return True
        
    except Exception as e:
        print(f"❌ List models failed: {e}")
        return False

def test_music_generation(prompt="upbeat electronic music", duration=5.0):
    """Test music generation endpoint."""
    print(f"🎵 Testing music generation...")
    print(f"   Prompt: '{prompt}'")
    print(f"   Duration: {duration} seconds")
    
    try:
        # Prepare request data
        request_data = {
            "prompt": prompt,
            "duration": duration,
            "temperature": 1.0,
            "cfg_coef": 3.0,
            "model_size": "small"  # Use small model for faster testing
        }
        
        print("   Sending request...")
        start_time = time.time()
        
        response = requests.post(
            ENDPOINTS["generate"],
            json=request_data,
            timeout=300  # 5 minutes timeout
        )
        
        end_time = time.time()
        generation_time = end_time - start_time
        
        response.raise_for_status()
        data = response.json()
        
        if data.get("success"):
            print(f"✅ Music generation successful!")
            print(f"   Generation time: {generation_time:.1f} seconds")
            print(f"   Model used: {data.get('model')}")
            print(f"   Audio format: {data.get('format')}")
            
            # Decode and save audio
            audio_data = data.get("audio_data")
            if audio_data:
                audio_bytes = base64.b64decode(audio_data)
                
                # Save to file
                output_file = Path(f"generated_music_{int(time.time())}.wav")
                output_file.write_bytes(audio_bytes)
                
                print(f"   Audio saved to: {output_file}")
                print(f"   File size: {len(audio_bytes):,} bytes")
                
                return True
            else:
                print("❌ No audio data received")
                return False
        else:
            print(f"❌ Music generation failed: {data.get('error')}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (>5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Music generation failed: {e}")
        return False

def main():
    """Run all endpoint tests."""
    print("🎵 Testing Modal MusicGen Service Endpoints")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health),
        ("List Models", test_list_models), 
        ("Music Generation", lambda: test_music_generation("happy upbeat electronic dance music", 3.0))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All endpoint tests passed!")
        print("\nYour MusicGen service is fully functional and ready to use.")
        print(f"\nEndpoint URLs:")
        for name, url in ENDPOINTS.items():
            print(f"  {name}: {url}")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
