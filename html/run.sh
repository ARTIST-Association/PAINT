#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv
AVAILABLE_PATH=/etc/apache2/sites-available
ENABLED_PATH=/etc/apache2/sites-enabled

# Activate virtual environment.
source $ENV_PATH/bin/activate

# Navigate to html directory.
cd ${PAINT_ROOT}/html || exit 1

# Copy configuration files to correct folder.
sudo cp paint_domain.conf $AVAILABLE_PATH/paint_domain.conf
sudo cp paint_domain-le-ssl.conf $AVAILABLE_PATH/paint_domain-le-ssl.conf

# Create symlinks in enabled folder.
sudo ln -sf $AVAILABLE_PATH/paint_domain.conf $ENABLED_PATH/paint_domain.conf
sudo ln -sf $AVAILABLE_PATH/paint_domain-le-ssl.conf $ENABLED_PATH/paint_domain-le-ssl.conf

# Kill flask application.
kill $(ps aux | grep '[p]ython wsgi.py' | awk '{print $2}')

# Start flask application.
python wsgi.py &

# Restart apache.
sudo systemctl restart apache2
