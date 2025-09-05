# 🎵 MusicGen Docker Setup

A complete Docker-based setup for running Meta's MusicGen AI model for music generation. This setup ensures consistent deployment across different machines and platforms.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://docker.com)
[![Python](https://img.shields.io/badge/Python-3.11-green?logo=python)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1.0-orange?logo=pytorch)](https://pytorch.org)
[![MusicGen](https://img.shields.io/badge/MusicGen-Ready-purple)](https://github.com/facebookresearch/audiocraft)

## 🚀 Quick Start with Docker

### Prerequisites
- Docker & Docker Compose installed
- At least 8GB RAM (16GB recommended)  
- 10GB free disk space for models

### 1. Clone and Run
```bash
git clone https://github.com/yourusername/musicgen-docker.git
cd musicgen-docker

# Run the test script (generates 3 sample clips)
docker-compose up musicgen
```

### 2. Generate Custom Music
```bash
# Generate custom music with interactive container
docker-compose run --rm musicgen python musicgen_advanced.py \
  --prompt "jazz piano with drums" \
  --duration 30 \
  --model small
```

### 3. Access Generated Files
Generated music files will be available in the `./generated_music/` directory on your host machine.

---

## 📖 Detailed Documentation

### Docker Commands

#### Basic Usage
```bash
# Build the container
docker-compose build

# Run test generation (3 sample clips)
docker-compose up musicgen

# Run interactive container
docker-compose run --rm musicgen bash
```

#### Advanced Generation
```bash
# Generate with different models
docker-compose run --rm musicgen python musicgen_advanced.py \
  -p "upbeat electronic dance music" -m medium -d 60

# Generate multiple clips
docker-compose run --rm musicgen python test_musicgen.py
```

### Available Models

| Model | Parameters | Memory | Speed | Quality | Docker Command |
|-------|------------|--------|-------|---------|----------------|
| `small` | 300M | ~3GB | ⚡ Fast | ✅ Good | `-m small` |
| `medium` | 1.5B | ~8GB | 🔄 Medium | ✅✅ Better | `-m medium` |
| `large` | 3.3B | ~15GB | 🐌 Slower | ✅✅✅ Best | `-m large` |

### Script Parameters

#### `musicgen_advanced.py` Options
```bash
--prompt, -p      Text description of music (required)
--duration, -d    Duration in seconds (default: 30)
--model, -m       Model size: small/medium/large (default: small)
--output, -o      Output directory (default: generated_music)
--filename, -f    Custom filename (optional)
--temperature     Sampling temperature (default: 1.0)
--top-k          Top-k sampling (default: 250)
--top-p          Top-p sampling (default: 0.0)
--cfg-coef       Classifier-free guidance (default: 3.0)
```

### Example Prompts
```bash
# Different genres
"jazz piano with brushed drums and upright bass"
"80s synthwave with arpeggiated synthesizers"
"classical violin and piano duet in minor key"
"lofi hip hop with vinyl crackling and mellow piano"
"country music with acoustic guitar and harmonica"
"ambient electronic soundscape with soft pads"
"rock music with distorted electric guitar and drums"
"orchestral movie soundtrack with epic brass section"
```

---

## 🛠️ Local Development (without Docker)

### Prerequisites
- Python 3.11
- 8-16GB RAM
- CUDA GPU (optional, will use CPU otherwise)

### Setup
```bash
# Create virtual environment
python3.11 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python test_musicgen.py
```

### Usage
```bash
# Generate custom music
python musicgen_advanced.py -p "upbeat jazz" -d 30 -m small

# Multiple test clips
python test_musicgen.py
```

---

## 📁 Project Structure

```
musicgen-docker/
├── 📄 Dockerfile              # Container definition
├── 📄 docker-compose.yml      # Multi-service setup
├── 📄 requirements.txt        # Python dependencies
├── 📄 .dockerignore           # Files to exclude from build
├── 🐍 test_musicgen.py       # Simple test script
├── 🐍 musicgen_advanced.py   # Advanced generation script
├── 📁 generated_music/        # Output directory (auto-created)
├── 📁 models/                 # Model cache (auto-created)
└── 📄 README.md              # This file
```

---

## 🎯 Performance & Requirements

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB | 20GB+ |
| **CPU** | 4 cores | 8+ cores |
| **GPU** | None (CPU works) | CUDA-compatible |

### Generation Times (Approximate)

| Duration | Small Model | Medium Model | Large Model |
|----------|-------------|--------------|-------------|
| 10s | ~30 seconds | ~2 minutes | ~5 minutes |
| 30s | ~1 minute | ~5 minutes | ~10 minutes |
| 60s | ~2 minutes | ~10 minutes | ~20 minutes |

*Times vary based on hardware and prompt complexity*

---

## 🔧 Troubleshooting

### Common Issues

**"Out of memory" errors:**
```bash
# Use smaller model
docker-compose run --rm musicgen python musicgen_advanced.py -p "music" -m small

# Reduce duration
docker-compose run --rm musicgen python musicgen_advanced.py -p "music" -d 15
```

**Slow generation:**
```bash
# Use small model for testing
-m small

# Reduce duration for quick tests
-d 10
```

**Container build fails:**
```bash
# Clean rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
```

**Models not downloading:**
- Check internet connection
- Verify disk space (models are ~1-3GB each)
- Try running container with `-it` flag for better error visibility

### Getting Help

1. **Check logs**: `docker-compose logs musicgen`
2. **Interactive debugging**: `docker-compose run --rm musicgen bash`
3. **Resource monitoring**: `docker stats`

---

## 🎵 Usage Tips

### Writing Good Prompts
- **Be specific**: "jazz piano trio" vs "music"
- **Include genre**: "country", "electronic", "classical"
- **Add instruments**: "acoustic guitar", "synthesizer", "drums"
- **Describe mood**: "upbeat", "melancholy", "energetic"
- **Add style**: "80s style", "lofi", "orchestral"

### Model Selection Guide
- **Small**: Quick testing, iterations, low resource usage
- **Medium**: Best balance of quality and speed for production
- **Large**: Highest quality, use for final outputs

### Parameter Tuning
- **Temperature** (0.1-2.0): Higher = more creative, lower = more focused
- **CFG Coefficient** (1.0-10.0): Higher = follows prompt more strictly
- **Top-k/Top-p**: Advanced sampling parameters for fine control

---

## 🚢 Deployment

### Production Considerations
- Use `large` model for best quality
- Mount persistent volumes for model caching
- Configure resource limits based on hardware
- Consider GPU support for faster generation

### Cloud Deployment
```bash
# Example for cloud deployment
docker run -d \
  --name musicgen \
  -v $(pwd)/generated_music:/app/generated_music \
  -v musicgen-models:/app/models \
  your-registry/musicgen:latest
```

---

## 📝 License

This project uses Meta's AudioCraft/MusicGen model. Please refer to the [AudioCraft License](https://github.com/facebookresearch/audiocraft/blob/main/LICENSE) for terms of use.

---

## 🙏 Credits

- **Meta AI**: For the amazing [AudioCraft](https://github.com/facebookresearch/audiocraft) and MusicGen models
- **PyTorch**: For the deep learning framework
- **Hugging Face**: For model hosting and utilities

---

**🎉 Ready to create AI music? Start with `docker-compose up musicgen`!** 🎶
