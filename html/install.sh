#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv

# Install git.
sudo apt-get update
sudo apt-get -y install git

# Check if repository exists, if not clone, if it exists pull.
if [ ! -d "$PAINT_ROOT" ]; then
  git clone https://github.com/ARTIST-Association/PAINT.git $PAINT_ROOT
else
  git pull
fi

# Navigate to repository and create virtual environment if it doesn't exist yet.
cd $PAINT_ROOT
if [ ! -d "$ENV_PATH" ]; then
  python3 -m venv $ENV_PATH
fi

# Activate virtual environment and upgrade pip.
source $ENV_PATH/bin/activate
pip install --upgrade pip

# Install dependencies.
pip install .
