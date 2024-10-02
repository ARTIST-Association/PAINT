#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv
AVAILABLE_PATH=/etc/apache2/sites-available
ENABLED_PATH=/etc/apache2/sites-enabled

# Activate virtual environment.
source $ENV_PATH/bin/activate

# Navigate to html directory.
cd ${PAINT_ROOT}/html || exit 1

# Copy configuration files to correct folder
cp
# Start flask application.
python wsgi.py &

# Restart apache.
sudo systemctl restart apache2
