#!/bin/bash

# if the dir doesn't exist, create it
if [ ! -d "$HOME/Omniplexium-Eternal" ]; then
  cd "$HOME"
  git clone https://github.com/Eli-Mason/Omniplexium-Eternal
fi

cd "$HOME/Omniplexium-Eternal"

rm -rf .venv

python3 -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

# Pull latest changes from GitHub
git pull

# Run the bot
python3 main.py