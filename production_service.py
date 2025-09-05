"""
Production-ready Modal service for MusicGen using Hugging Face Transformers.
This approach avoids AudioCraft compatibility issues.
"""

import io
import os
import base64
from typing import Dict
import modal

app = modal.App("musicgen-production")

# Use Hugging Face transformers which has better compatibility
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install([
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "transformers>=4.30.0", 
        "scipy>=1.9.0",
        "fastapi>=0.100.0",
        "pydantic>=2.0.0",
    ])
    .apt_install(["git", "ffmpeg"])
)

volume = modal.Volume.from_name("musicgen-hf-models", create_if_missing=True)

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "musicgen-production"}

@app.function(image=image)
@modal.fastapi_endpoint(method="GET")
def list_models():
    """List available MusicGen models."""
    return {
        "models": [
            {
                "id": "small",
                "name": "MusicGen Small",
                "hf_model": "facebook/musicgen-small",
                "description": "Fastest generation, good quality"
            },
            {
                "id": "medium", 
                "name": "MusicGen Medium",
                "hf_model": "facebook/musicgen-medium",
                "description": "Balanced speed and quality"
            },
            {
                "id": "large",
                "name": "MusicGen Large",
                "hf_model": "facebook/musicgen-large", 
                "description": "Best quality, slower generation"
            }
        ]
    }

@app.function(image=image, gpu="A10G", volumes={"/models": volume}, timeout=600)
@modal.fastapi_endpoint(method="POST")
def generate_music(request_data: Dict):
    """Generate music using Hugging Face Transformers MusicGen."""
    import torch
    import torchaudio
    from transformers import MusicgenForConditionalGeneration, AutoProcessor
    from pydantic import BaseModel, Field
    
    class GenerateRequest(BaseModel):
        prompt: str = Field(..., min_length=1, max_length=500)
        duration: float = Field(default=10.0, gt=0, le=30)
        model_size: str = Field(default="small", pattern="^(small|medium|large)$")
    
    try:
        # Validate request
        req = GenerateRequest(**request_data)
        
        # Map model sizes to Hugging Face model names
        model_map = {
            "small": "facebook/musicgen-small",
            "medium": "facebook/musicgen-medium",
            "large": "facebook/musicgen-large"
        }
        
        model_name = model_map[req.model_size]
        cache_dir = "/models/musicgen-hf"
        os.makedirs(cache_dir, exist_ok=True)
        
        print(f"Loading model: {model_name}")
        
        # Load model and processor
        processor = AutoProcessor.from_pretrained(model_name, cache_dir=cache_dir)
        model = MusicgenForConditionalGeneration.from_pretrained(
            model_name, 
            cache_dir=cache_dir,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        
        print("Model loaded successfully")
        
        # Process inputs
        inputs = processor(
            text=[req.prompt],
            padding=True,
            return_tensors="pt",
        )
        
        # Calculate the number of tokens for the duration
        # MusicGen typically generates ~50 tokens per second
        max_new_tokens = int(req.duration * 50)
        
        print(f"Generating {req.duration}s of audio ({max_new_tokens} tokens)")
        
        # Generate audio
        with torch.no_grad():
            audio_values = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                guidance_scale=3.0,
            )
        
        # Convert to audio
        audio_data = audio_values[0].cpu().float()
        sample_rate = model.config.audio_encoder.sampling_rate
        
        print(f"Generated audio shape: {audio_data.shape}, sample rate: {sample_rate}")
        
        # Normalize audio
        if audio_data.abs().max() > 0:
            audio_data = audio_data / audio_data.abs().max()
        
        # Convert to bytes
        buffer = io.BytesIO()
        torchaudio.save(
            buffer,
            audio_data.unsqueeze(0),
            sample_rate=sample_rate,
            format="wav"
        )
        
        audio_bytes = buffer.getvalue()
        audio_b64 = base64.b64encode(audio_bytes).decode()
        
        return {
            "success": True,
            "audio_data": audio_b64,
            "format": "wav", 
            "duration": req.duration,
            "sample_rate": sample_rate,
            "prompt": req.prompt,
            "model": req.model_size
        }
        
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    print("MusicGen Production Service (Hugging Face)")
    print("Deploy with: modal deploy production_service.py")
