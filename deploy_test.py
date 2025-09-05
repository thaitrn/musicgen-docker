#!/usr/bin/env python3
"""
Simple deployment test for the MusicGen Modal service.
This script validates that the service can be deployed to Modal.
"""

import subprocess
import sys
from pathlib import Path

def validate_modal_setup():
    """Validate Modal is properly configured."""
    try:
        # Check Modal installation
        import modal
        print(f"✅ Modal version: {modal.__version__}")
        
        # Test Modal authentication by trying to list apps
        result = subprocess.run(
            ["modal", "app", "list"], 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Modal authentication verified")
            return True
        else:
            print("❌ Modal authentication failed")
            print(f"Error: {result.stderr}")
            return False
            
    except ImportError:
        print("❌ Modal not installed")
        return False
    except Exception as e:
        print(f"❌ Modal validation failed: {e}")
        return False

def check_service_file():
    """Check that the service file exists and looks correct."""
    service_file = Path("modal_service.py")
    
    if not service_file.exists():
        print("❌ modal_service.py not found")
        return False
    
    print("✅ Service file found")
    
    # Basic syntax check
    try:
        with open(service_file) as f:
            content = f.read()
            
        # Check for required components
        checks = [
            ("modal.App", "App definition"),
            ("@modal.fastapi_endpoint", "FastAPI endpoints"),
            ("MusicGenService", "Service class"),
            ("audiocraft", "AudioCraft import")
        ]
        
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description} found")
            else:
                print(f"⚠️  {description} not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading service file: {e}")
        return False

def test_deploy():
    """Test deployment to Modal."""
    try:
        print("🚀 Testing deployment to Modal...")
        
        # Try to deploy (this will validate syntax and dependencies)
        result = subprocess.run(
            ["modal", "deploy", "modal_service.py"],
            capture_output=True,
            text=True,
            timeout=180  # 3 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Deployment successful!")
            print("\nDeployment output:")
            print(result.stdout)
            return True
        else:
            print("❌ Deployment failed")
            print(f"Error output:\n{result.stderr}")
            print(f"Standard output:\n{result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Deployment timed out (>3 minutes)")
        return False
    except Exception as e:
        print(f"❌ Deployment test failed: {e}")
        return False

def main():
    """Run deployment validation."""
    print("🎵 MusicGen Modal Service - Deployment Test")
    print("=" * 50)
    
    # Step 1: Validate Modal setup
    print("\\n1. Validating Modal setup...")
    if not validate_modal_setup():
        print("\\n❌ Modal setup validation failed!")
        print("Please run: modal token new")
        return False
    
    # Step 2: Check service file
    print("\\n2. Checking service file...")
    if not check_service_file():
        print("\\n❌ Service file validation failed!")
        return False
    
    # Step 3: Test deployment
    print("\\n3. Testing deployment...")
    if not test_deploy():
        print("\\n❌ Deployment test failed!")
        print("\\nCommon issues:")
        print("- Check internet connection")
        print("- Verify Modal account has GPU access")
        print("- Check for syntax errors in modal_service.py")
        return False
    
    print("\\n🎉 All tests passed!")
    print("\\nYour MusicGen service has been deployed to Modal.")
    print("\\nNext steps:")
    print("1. Note down the endpoint URLs from the deployment output")
    print("2. Update your environment variables with the service URL")
    print("3. Test the service with HTTP requests")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
