#!/bin/bash

echo "🎵 Testing music generation endpoint with curl..."

curl -X POST "https://tranthai0414--musicgen-service-generate.modal.run" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "happy upbeat electronic music",
    "duration": 3.0,
    "temperature": 1.0,
    "cfg_coef": 3.0,
    "model_size": "small"
  }' \
  --max-time 300 \
  | python -m json.tool
