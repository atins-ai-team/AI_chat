#!/bin/bash

# Start Ollama in the background.
/bin/ollama serve &
# Record Process ID.
pid=$!

# Pause for Ollama to start.
sleep 5

echo " Retrieve $MODEL_MAIN model..."
ollama pull $MODEL_MAIN
echo " Done!"

echo " Retrieve $MODEL_EMBEDDING model..."
ollama pull $MODEL_EMBEDDING
echo " Done!"

# Wait for Ollama process to finish.
wait $pid