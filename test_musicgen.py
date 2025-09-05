#!/usr/bin/env python3
"""
Simple MusicGen Test Script
Generates a short music clip to test the installation
"""

import torch
import torchaudio
from audiocraft.models import MusicGen
import os
from datetime import datetime

def main():
    print("🎵 MusicGen Test Script")
    print("=" * 50)
    
    # Check device
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"Using device: {device}")
    print()
    
    try:
        # Load the small model (fastest for testing)
        print("📥 Loading MusicGen model...")
        print("(This may take a few minutes on first run - downloading model)")
        
        model = MusicGen.get_pretrained('facebook/musicgen-small')
        print("✅ Model loaded successfully!")
        print()
        
        # Set generation parameters
        duration = 10  # seconds (start short for testing)
        model.set_generation_params(duration=duration)
        
        # Music descriptions to try
        descriptions = [
            "upbeat electronic dance music with synthesizers",
            "peaceful acoustic guitar melody",
            "energetic rock music with drums and electric guitar"
        ]
        
        print(f"🎼 Generating {len(descriptions)} music clips ({duration}s each)...")
        print()
        
        # Create output directory
        output_dir = "generated_music"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate music for each description
        for i, description in enumerate(descriptions, 1):
            print(f"🎵 Generating clip {i}: '{description}'")
            
            # Generate the audio
            wav = model.generate([description], progress=True)
            
            # Create filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{output_dir}/musicgen_test_{i}_{timestamp}.wav"
            
            # Save the audio file
            # wav is shape (1, 1, sample_rate * duration)
            torchaudio.save(filename, wav[0].cpu(), model.sample_rate)
            
            print(f"✅ Saved: {filename}")
            print(f"   Duration: {duration}s")
            print(f"   Sample rate: {model.sample_rate}Hz")
            print()
        
        print("🎉 All clips generated successfully!")
        print(f"📁 Check the '{output_dir}' directory for your music files")
        print()
        print("💡 Tips:")
        print("- You can play the .wav files with any audio player")
        print("- Try different descriptions for different music styles")
        print("- Increase duration for longer clips (but it takes more time)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("🔧 Troubleshooting:")
        print("- Make sure you're in the virtual environment")
        print("- Check your internet connection (for model download)")
        print("- Try running: source env/bin/activate")

if __name__ == "__main__":
    main()
