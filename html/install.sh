#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv

# Install git.
sudo apt-get update
sudo apt-get -y install apache2 git python3-venv

# Enable apache proxy.
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod alias
sudo a2enmod cache

# Check if repository exists, if not clone, if it exists pull.
if [ ! -d "$PAINT_ROOT" ]; then
  git clone https://github.com/ARTIST-Association/PAINT.git $PAINT_ROOT
else
  cd "${PAINT_ROOT}" || exit 1
  git pull
fi

# Navigate to repository and create virtual environment if it doesn't exist yet.
cd "${PAINT_ROOT}" || exit 1
if [ ! -d "$ENV_PATH" ]; then
  python3 -m venv $ENV_PATH
fi

# Activate virtual environment and upgrade pip.
source $ENV_PATH/bin/activate
pip install --upgrade pip

# Install dependencies.
pip install --upgrade .
