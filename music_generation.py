import modal
from pydantic import BaseModel
from typing import Optional, List

app = modal.App("opencut-music-generation")

class MusicGenerationRequest(BaseModel):
    prompt: str
    duration: Optional[float] = 10.0  # Duration in seconds (default 10s)
    model_size: Optional[str] = "medium"  # small, medium, large
    top_k: Optional[int] = 250
    top_p: Optional[float] = 0.0
    temperature: Optional[float] = 1.0
    cfg_coeff: Optional[float] = 3.0  # Classifier Free Guidance coefficient
    output_filename: Optional[str] = None  # If provided, will upload to R2

class MusicGenerationResponse(BaseModel):
    success: bool
    audio_url: Optional[str] = None
    filename: Optional[str] = None
    duration: Optional[float] = None
    prompt: str
    error: Optional[str] = None

@app.function(
    image=modal.Image.from_registry("pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime")
        .apt_install(["ffmpeg", "git"])
        .pip_install([
            "audiocraft==1.3.0",
            "torch>=2.1.0",
            "torchaudio>=2.1.0", 
            "fastapi[standard]>=0.100.0",
            "pydantic>=2.0.0",
            "boto3>=1.26.0",
            "cryptography>=3.4.8",
            "librosa>=0.9.0",
            "numpy",
            "scipy"
        ]),
    gpu=modal.gpu.A10G(),  # AudioCraft requires decent GPU for inference
    timeout=600,  # 10 minutes timeout
    secrets=[modal.Secret.from_name("opencut-r2-secrets")]
)
@modal.fastapi_endpoint(method="POST")
def generate_music(request: MusicGenerationRequest):
    import tempfile
    import os
    import traceback
    import torch
    import torchaudio
    import boto3
    from audiocraft.models import MusicGen
    import time
    import uuid
    
    try:
        print(f"Starting music generation with prompt: {request.prompt}")
        print(f"Model size: {request.model_size}, Duration: {request.duration}s")
        
        # Load the MusicGen model
        model_name_map = {
            "small": "facebook/musicgen-small",
            "medium": "facebook/musicgen-medium", 
            "large": "facebook/musicgen-large"
        }
        
        model_name = model_name_map.get(request.model_size, "facebook/musicgen-medium")
        print(f"Loading model: {model_name}")
        
        model = MusicGen.get_pretrained(model_name)
        
        # Set generation parameters
        model.set_generation_params(
            duration=request.duration,
            top_k=request.top_k,
            top_p=request.top_p,
            temperature=request.temperature,
            cfg_coeff=request.cfg_coeff,
        )
        
        print("Generating music...")
        start_time = time.time()
        
        # Generate music
        descriptions = [request.prompt]
        wav = model.generate(descriptions)  # wav shape: [1, 1, sample_rate * duration]
        
        generation_time = time.time() - start_time
        print(f"Music generated in {generation_time:.2f} seconds")
        
        # Create temporary file for the generated audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_path = temp_file.name
            
            # Save the generated audio
            # wav is a torch tensor with shape [1, 1, samples]
            sample_rate = model.sample_rate
            torchaudio.save(temp_path, wav[0].cpu(), sample_rate)
            
            print(f"Audio saved to temporary file: {temp_path}")
            
            # If output_filename is provided, upload to R2
            audio_url = None
            filename = request.output_filename
            
            if filename:
                try:
                    # Initialize R2 client
                    s3_client = boto3.client(
                        's3',
                        endpoint_url=f'https://{os.environ["CLOUDFLARE_ACCOUNT_ID"]}.r2.cloudflarestorage.com',
                        aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
                        region_name='auto'
                    )
                    
                    # Upload to R2
                    bucket_name = os.environ["R2_BUCKET_NAME"]
                    s3_client.upload_file(temp_path, bucket_name, filename)
                    
                    # Generate public URL (note: you may need to configure R2 for public access)
                    audio_url = f"https://{bucket_name}.{os.environ['CLOUDFLARE_ACCOUNT_ID']}.r2.cloudflarestorage.com/{filename}"
                    print(f"Audio uploaded to R2: {audio_url}")
                    
                except Exception as upload_error:
                    print(f"Failed to upload to R2: {str(upload_error)}")
                    # Continue without upload - we'll still return the success
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
            return MusicGenerationResponse(
                success=True,
                audio_url=audio_url,
                filename=filename,
                duration=request.duration,
                prompt=request.prompt
            ).model_dump()
            
    except Exception as e:
        error_msg = str(e)
        print(f"Music generation error: {error_msg}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return MusicGenerationResponse(
            success=False,
            prompt=request.prompt,
            error=error_msg
        ).model_dump()

@app.function(
    image=modal.Image.from_registry("pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime")
        .apt_install(["ffmpeg"])
        .pip_install([
            "audiocraft==1.3.0",
            "torch>=2.1.0",
            "fastapi[standard]>=0.100.0",
            "pydantic>=2.0.0"
        ]),
    timeout=60
)
@modal.fastapi_endpoint(method="GET", path="/health")
def health_check():
    """Health check endpoint for the music generation service"""
    return {"status": "healthy", "service": "opencut-music-generation"}

@app.function(
    image=modal.Image.from_registry("pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime")
        .pip_install([
            "audiocraft==1.3.0",
            "torch>=2.1.0"
        ]),
    timeout=120
)
@modal.fastapi_endpoint(method="GET", path="/models")
def list_models():
    """List available MusicGen models"""
    return {
        "models": [
            {
                "name": "small",
                "description": "MusicGen Small - Fast generation, good quality",
                "parameters": "300M"
            },
            {
                "name": "medium", 
                "description": "MusicGen Medium - Balance of speed and quality",
                "parameters": "1.5B"
            },
            {
                "name": "large",
                "description": "MusicGen Large - Best quality, slower generation", 
                "parameters": "3.3B"
            }
        ]
    }

@app.local_entrypoint()
def main():
    """Test function - you can call this with modal run music_generation.py"""
    print("Music Generation service is ready to deploy!")
    print("Deploy with: modal deploy music_generation.py")
    print("\nAvailable endpoints:")
    print("- POST / : Generate music from text prompt")
    print("- GET /health : Health check")
    print("- GET /models : List available models")
