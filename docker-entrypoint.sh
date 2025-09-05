#!/bin/bash
set -e

# Docker entrypoint script for MusicGen container
echo "🎵 MusicGen Docker Container Starting..."

# Create directories if they don't exist
mkdir -p /app/generated_music
mkdir -p /app/models

# Set proper permissions
chown -R $(id -u):$(id -g) /app/generated_music /app/models 2>/dev/null || true

# Print system info
echo "🖥️  Container System Info:"
echo "   CPU cores: $(nproc)"
echo "   Memory: $(free -h | awk '/^Mem:/ {print $2}')"
echo "   Disk space: $(df -h /app | awk 'NR==2 {print $4}') available"
echo "   Python version: $(python --version)"

# Check if models directory is mounted/populated
if [ -d "/app/models" ] && [ "$(ls -A /app/models 2>/dev/null)" ]; then
    echo "✅ Models directory found with cached models"
else
    echo "📥 Models will be downloaded on first run (may take time)"
fi

# Print available commands
echo ""
echo "🚀 Available commands:"
echo "   python test_musicgen.py                    # Generate 3 test clips"
echo "   python musicgen_advanced.py -p 'prompt'   # Custom generation"
echo "   bash                                       # Interactive shell"
echo ""

# Execute the command passed to docker run
exec "$@"
