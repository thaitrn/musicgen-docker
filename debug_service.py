"""
Debug version of the Modal service to test AudioCraft step by step.
"""

import modal

# Create the Modal app
app = modal.App("musicgen-debug")

# Define the Modal image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install([
        "torch==2.1.0",
        "torchaudio==2.1.0", 
        "transformers>=4.30.0",
        "audiocraft",
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
    ])
    .apt_install(["git", "ffmpeg"])
)

# Define shared volume for model caching
volume = modal.Volume.from_name("musicgen-models", create_if_missing=True)

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "musicgen-debug"}

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def test_imports():
    """Test importing required libraries."""
    try:
        import torch
        import torchaudio
        import transformers
        
        result = {
            "success": True,
            "torch_version": torch.__version__,
            "torchaudio_version": torchaudio.__version__,
            "transformers_version": transformers.__version__,
            "cuda_available": torch.cuda.is_available()
        }
        
        # Try importing audiocraft
        try:
            import audiocraft
            result["audiocraft_version"] = getattr(audiocraft, '__version__', 'unknown')
            result["audiocraft_available"] = True
        except Exception as e:
            result["audiocraft_available"] = False
            result["audiocraft_error"] = str(e)
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@app.function(image=image, gpu="A10G", volumes={"/models": volume}, timeout=180)
@modal.fastapi_endpoint(method="GET") 
def test_model_loading():
    """Test loading the AudioCraft model."""
    try:
        import torch
        from audiocraft.models import MusicGen
        import os
        
        print("Testing model loading...")
        
        # Setup cache directory
        cache_dir = "/models/musicgen"
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"Cache directory: {cache_dir}")
        
        # Try to load the small model
        model_name = "facebook/musicgen-small"
        print(f"Loading model: {model_name}")
        
        model = MusicGen.get_pretrained(model_name, cache_dir=cache_dir)
        
        print("Model loaded successfully!")
        
        return {
            "success": True,
            "model_name": model_name,
            "sample_rate": model.sample_rate,
            "compression_model": str(type(model.compression_model)),
            "text_encoder": str(type(model.text_encoder))
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
def test_generation(request_data: dict):
    """Test a simple music generation."""
    try:
        import torch
        from audiocraft.models import MusicGen
        import os
        import base64
        import io
        import torchaudio
        
        prompt = request_data.get("prompt", "happy music")
        duration = request_data.get("duration", 2.0)  # Very short for testing
        
        print(f"Testing generation: '{prompt}' for {duration}s")
        
        # Setup cache directory
        cache_dir = "/models/musicgen"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load the small model
        model_name = "facebook/musicgen-small"
        model = MusicGen.get_pretrained(model_name, cache_dir=cache_dir)
        
        # Set generation parameters
        model.set_generation_params(duration=duration)
        
        print("Generating audio...")
        
        # Generate music
        with torch.no_grad():
            wav = model.generate([prompt])
        
        print(f"Generated tensor shape: {wav.shape}")
        
        # Convert tensor to audio bytes
        audio_tensor = wav[0].squeeze().cpu()
        
        # Normalize audio
        if audio_tensor.abs().max() > 0:
            audio_tensor = audio_tensor / audio_tensor.abs().max()
        
        # Convert to bytes
        buffer = io.BytesIO()
        torchaudio.save(
            buffer, 
            audio_tensor.unsqueeze(0), 
            sample_rate=model.sample_rate,
            format="wav"
        )
        
        audio_bytes = buffer.getvalue()
        print(f"Generated audio bytes: {len(audio_bytes)}")
        
        # Return just the size for now, not the full audio data
        return {
            "success": True,
            "prompt": prompt,
            "duration": duration,
            "audio_size_bytes": len(audio_bytes),
            "sample_rate": model.sample_rate,
            "tensor_shape": str(wav.shape)
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    print("MusicGen Debug Service")
    print("Deploy with: modal deploy debug_service.py")
