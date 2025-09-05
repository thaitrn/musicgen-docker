"""
Simple Modal service for AudioCraft MusicGen music generation.
This service downloads the MusicGen model and provides endpoints to generate music from text prompts.
"""

import io
import os
from typing import Dict
import modal

# Create the Modal app
app = modal.App("musicgen-service")

# Define the Modal image with required dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install([
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "transformers>=4.30.0",
        "audiocraft",
        "fastapi>=0.100.0",
        "boto3>=1.26.0",
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
    return {"status": "healthy", "service": "musicgen"}

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def list_models():
    """List available models."""
    return {
        "models": [
            {
                "id": "small",
                "name": "MusicGen Small",
                "description": "Fastest generation, good quality"
            },
            {
                "id": "medium", 
                "name": "MusicGen Medium",
                "description": "Balanced speed and quality"
            },
            {
                "id": "large",
                "name": "MusicGen Large", 
                "description": "Best quality, slower generation"
            }
        ]
    }

@app.function(image=image, gpu="A10G", volumes={"/models": volume}, timeout=600)
@modal.fastapi_endpoint(method="POST")
def generate(request_data: Dict):
    """Generate music endpoint."""
    import torch
    import torchaudio
    import base64
    import io
    from pydantic import BaseModel, Field
    from audiocraft.models import MusicGen
    
    class GenerateRequest(BaseModel):
        prompt: str = Field(..., min_length=1, max_length=500)
        duration: float = Field(default=10.0, gt=0, le=30)
        temperature: float = Field(default=1.0, gt=0, le=2.0)
        cfg_coef: float = Field(default=3.0, gt=0, le=10.0)
        model_size: str = Field(default="small", pattern="^(small|medium|large)$")
    
    try:
        # Validate request
        req = GenerateRequest(**request_data)
        
        print(f"Loading MusicGen model: {req.model_size}")
        
        # Map model sizes to actual model names
        model_map = {
            "small": "facebook/musicgen-small",
            "medium": "facebook/musicgen-medium", 
            "large": "facebook/musicgen-large"
        }
        
        model_name = model_map.get(req.model_size, "facebook/musicgen-small")
        
        # Load the model with caching in the volume
        cache_dir = "/models/musicgen"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Load model from cache or download
        model = MusicGen.get_pretrained(model_name, cache_dir=cache_dir)
        print(f"Successfully loaded {model_name}")
        
        # Set generation parameters
        model.set_generation_params(
            duration=req.duration,
            temperature=req.temperature,
            cfg_coef=req.cfg_coef
        )
        
        print(f"Generating music for prompt: '{req.prompt}'")
        print(f"Duration: {req.duration}s, Temperature: {req.temperature}, CFG: {req.cfg_coef}")
        
        # Generate music
        with torch.no_grad():
            wav = model.generate([req.prompt])
        
        # Convert tensor to audio bytes
        audio_tensor = wav[0].squeeze().cpu()  # Remove batch dimension and move to CPU
        
        # Normalize audio to prevent clipping
        if audio_tensor.abs().max() > 0:
            audio_tensor = audio_tensor / audio_tensor.abs().max()
        
        # Convert to bytes using torchaudio
        buffer = io.BytesIO()
        torchaudio.save(
            buffer, 
            audio_tensor.unsqueeze(0),  # Add channel dimension
            sample_rate=model.sample_rate,
            format="wav"
        )
        
        audio_bytes = buffer.getvalue()
        print(f"Generated audio: {len(audio_bytes)} bytes")
        
        # Return base64 encoded audio
        audio_b64 = base64.b64encode(audio_bytes).decode()
        
        return {
            "success": True,
            "audio_data": audio_b64,
            "format": "wav",
            "duration": req.duration,
            "prompt": req.prompt,
            "model": req.model_size
        }
        
    except Exception as e:
        import traceback
        print(f"Error in generate: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    # For local testing
    print("MusicGen Modal Service")
    print("Deploy with: modal deploy modal_service_fixed.py")
