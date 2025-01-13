#!/bin/bash

# if the dir doesn't exist, create it
if [ ! -d "$HOME/Omniplexium-Eternal" ]; then
  cd "$HOME"
  git clone https://github.com/Eli-Mason/Omniplexium-Eternal
fi

cd "$HOME/Omniplexium-Eternal"

# if we have a virtual environment, deactivate it
if [ -n "$VIRTUAL_ENV" ]; then
  deactivate
fi

source .venv/bin/activate

# Pull latest changes from GitHub
git pull

# Run the bot
python3 main.py