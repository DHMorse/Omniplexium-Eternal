#!/bin/bash

# if the dir doesn't exist, create it
if [ ! -d "~/Omniplexium-Eternal" ]; then
  cd ~/
  git clone https://github.com/Eli-Mason/Omniplexium-Eternal
fi

cd ~/Omniplexium-Eternal

# if we have a virtual environment, deactivate it
if [ -d ".venv" ]; then
  deactivate
fi

source .venv/bin/activate

# Pull latest changes from GitHub
git pull

# Run the bot
python3 main.py