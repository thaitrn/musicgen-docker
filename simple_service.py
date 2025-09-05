"""
Simple working Modal service for MusicGen without complex dependencies.
"""

import modal
import os

app = modal.App("simple-musicgen")

# Use a simpler approach with pinned versions that are known to work together
image = (
    modal.Image.debian_slim(python_version="3.9")
    .pip_install([
        "torch==1.13.1",
        "torchaudio==0.13.1", 
        "transformers==4.21.0",
        "scipy",
        "librosa",
        "audiocraft==1.0.0a",  # Use the alpha version which is more stable
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
    ])
    .apt_install(["git", "ffmpeg"])
)

volume = modal.Volume.from_name("simple-musicgen", create_if_missing=True)

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def health():
    return {"status": "healthy", "service": "simple-musicgen"}

@app.function(image=image)
@modal.fastapi_endpoint(method="GET") 
def test_basic_imports():
    """Test basic imports without loading models."""
    try:
        import torch
        import torchaudio
        print(f"PyTorch version: {torch.__version__}")
        print(f"TorchAudio version: {torchaudio.__version__}")
        
        # Test if CUDA is available
        cuda_available = torch.cuda.is_available()
        print(f"CUDA available: {cuda_available}")
        
        return {
            "success": True,
            "torch_version": torch.__version__,
            "torchaudio_version": torchaudio.__version__,
            "cuda_available": cuda_available
        }
        
    except Exception as e:
        return {
            "success": False, 
            "error": str(e)
        }

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def test_audiocraft_imports():
    """Test AudioCraft imports specifically."""
    try:
        print("Testing audiocraft imports...")
        
        # Try importing audiocraft step by step
        import audiocraft
        print(f"AudioCraft imported successfully")
        
        from audiocraft.models import MusicGen
        print(f"MusicGen imported successfully")
        
        return {
            "success": True,
            "audiocraft_available": True,
            "message": "All imports successful"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

@app.function(image=image, gpu="A10G", volumes={"/models": volume}, timeout=300)
@modal.fastapi_endpoint(method="POST")
def simple_generation_test():
    """Try a very basic generation test.""" 
    try:
        import torch
        from audiocraft.models import MusicGen
        import base64
        import io
        
        print("Loading model...")
        
        # Try to load the smallest model
        model = MusicGen.get_pretrained('small')
        print(f"Model loaded: {type(model)}")
        
        # Very short generation
        model.set_generation_params(duration=2.0)
        
        print("Generating audio...")
        with torch.no_grad():
            wav = model.generate(['happy music'])
        
        print(f"Generated tensor shape: {wav.shape}")
        
        # Convert to basic format
        audio_tensor = wav[0].squeeze(0).cpu().numpy()
        
        return {
            "success": True,
            "tensor_shape": str(wav.shape),
            "audio_length": len(audio_tensor),
            "sample_rate": model.sample_rate
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    print("Simple MusicGen Service")
    print("Deploy with: modal deploy simple_service.py")
