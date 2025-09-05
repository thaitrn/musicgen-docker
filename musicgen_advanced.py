#!/usr/bin/env python3
"""
Advanced MusicGen Script
More customizable music generation with different models and parameters
"""

import torch
import torchaudio
from audiocraft.models import MusicGen
import os
import argparse
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Generate music with MusicGen')
    parser.add_argument('--prompt', '-p', type=str, required=True,
                        help='Text description of the music to generate')
    parser.add_argument('--duration', '-d', type=int, default=30,
                        help='Duration in seconds (default: 30)')
    parser.add_argument('--model', '-m', type=str, default='small',
                        choices=['small', 'medium', 'large'],
                        help='Model size (default: small)')
    parser.add_argument('--output', '-o', type=str, default='generated_music',
                        help='Output directory (default: generated_music)')
    parser.add_argument('--filename', '-f', type=str, default=None,
                        help='Custom filename (default: auto-generated)')
    parser.add_argument('--top-k', type=int, default=250,
                        help='Top-k sampling parameter (default: 250)')
    parser.add_argument('--top-p', type=float, default=0.0,
                        help='Top-p sampling parameter (default: 0.0)')
    parser.add_argument('--temperature', type=float, default=1.0,
                        help='Temperature for sampling (default: 1.0)')
    parser.add_argument('--cfg-coef', type=float, default=3.0,
                        help='Classifier-free guidance coefficient (default: 3.0)')
    
    args = parser.parse_args()
    
    print("🎵 Advanced MusicGen Script")
    print("=" * 50)
    print(f"Prompt: {args.prompt}")
    print(f"Duration: {args.duration}s")
    print(f"Model: {args.model}")
    print()
    
    # Check device
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    try:
        # Load the specified model
        model_name = f'facebook/musicgen-{args.model}'
        print(f"📥 Loading model: {model_name}")
        print("(This may take a while for medium/large models)")
        
        model = MusicGen.get_pretrained(model_name)
        print("✅ Model loaded successfully!")
        
        # Set generation parameters
        model.set_generation_params(
            duration=args.duration,
            top_k=args.top_k,
            top_p=args.top_p,
            temperature=args.temperature,
            cfg_coef=args.cfg_coef
        )
        
        print(f"🎼 Generation parameters:")
        print(f"  - Top-k: {args.top_k}")
        print(f"  - Top-p: {args.top_p}")
        print(f"  - Temperature: {args.temperature}")
        print(f"  - CFG coefficient: {args.cfg_coef}")
        print()
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Generate filename
        if args.filename:
            filename = f"{args.output}/{args.filename}.wav"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_prompt = "".join(c for c in args.prompt[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_prompt = safe_prompt.replace(' ', '_')
            filename = f"{args.output}/musicgen_{args.model}_{safe_prompt}_{timestamp}.wav"
        
        print(f"🎵 Generating music...")
        print(f"This will take approximately {args.duration // 5} minutes for {args.duration}s")
        
        # Generate the music
        wav = model.generate([args.prompt], progress=True)
        
        # Save the audio file
        torchaudio.save(filename, wav[0].cpu(), model.sample_rate)
        
        print(f"✅ Music generated successfully!")
        print(f"📁 Saved: {filename}")
        print(f"📊 File size: {os.path.getsize(filename) / (1024*1024):.1f} MB")
        print(f"🎶 Sample rate: {model.sample_rate}Hz")
        print(f"⏱️  Duration: {args.duration}s")
        
        # Print playback command
        print()
        print("🔊 To play the file:")
        print(f"   afplay \"{filename}\"")
        print("   or double-click the file to open in QuickTime/Music app")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
