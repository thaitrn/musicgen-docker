# 🚀 MusicGen Quick Deploy Guide

## One-Line Setup

```bash
# Clone and run in one command
git clone https://github.com/thaitrn/musicgen-docker.git && cd musicgen-docker && docker-compose up musicgen
```

## Step-by-Step

### 1. Clone the Repository
```bash
git clone https://github.com/thaitrn/musicgen-docker.git
cd musicgen-docker
```

### 2. Choose Your Method

#### Docker (Recommended)
```bash
# Build and run test (generates 3 sample clips)
docker-compose up musicgen

# Generate custom music
docker-compose run --rm musicgen python musicgen_advanced.py \
  --prompt "jazz piano with drums" --duration 30 --model small
```

#### Local Python Setup
```bash
# Create virtual environment
python3.11 -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Test installation
python test_musicgen.py
```

### 3. Access Generated Music
Your generated music files will be in:
- **Docker**: `./generated_music/` on your host machine
- **Local**: `./generated_music/` directory

### 4. Play Your Music
```bash
# macOS/Linux
afplay generated_music/your_file.wav

# Or double-click the files in your file explorer
```

## System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB+ |
| **Storage** | 10GB free | 20GB+ |
| **Internet** | For model downloads | Stable connection |

## Quick Examples

```bash
# Jazz music
docker-compose run --rm musicgen python musicgen_advanced.py -p "smooth jazz with saxophone" -d 30

# Electronic dance
docker-compose run --rm musicgen python musicgen_advanced.py -p "upbeat electronic dance music" -d 60 -m medium

# Classical piano
docker-compose run --rm musicgen python musicgen_advanced.py -p "classical piano sonata" -d 45 -m large
```

## Troubleshooting

**Out of memory?**
```bash
# Use smaller model
-m small

# Reduce duration
-d 15
```

**Docker build fails?**
```bash
# Clean rebuild
docker-compose down
docker system prune -a
docker-compose build --no-cache
```

**Models not downloading?**
- Check internet connection
- Verify 10GB+ free disk space
- Try with `-it` flag for better error visibility

## Support

- 📖 Full documentation: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/thaitrn/musicgen-docker/issues)
- 💡 Discussions: [GitHub Discussions](https://github.com/thaitrn/musicgen-docker/discussions)

---

**Ready to create AI music? Just run `docker-compose up musicgen`!** 🎶
