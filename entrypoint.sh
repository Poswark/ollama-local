#!/bin/bash
set -e

echo "Starting Ollama server..."
/bin/ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 10

# Check if model exists, if not pull it
echo "Checking for models..."
if ! /bin/ollama list | grep -q "gemma:2b"; then
    echo "Pulling gemma:2b model... (this may take a while)"
    /bin/ollama pull gemma:2b
else
    echo "Model gemma:2b already exists"
fi

echo "Starting FastAPI application..."
exec python3 main.py