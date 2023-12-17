#!/bin/bash
./script/background_ollama_server.sh

source /miniconda/bin/activate ${ENV_NAME}
cd libs
python -u streaming_runpod_server.py
exec "$@"