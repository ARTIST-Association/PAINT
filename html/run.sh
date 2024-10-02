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
cp paint_domain.conf $AVAILABLE_PATH/paint_domain.conf
cp paint_domain-le-ssl.conf $AVAILABLE_PATH/paint_domain-le-ssl.conf

# Create symlinks in enabled folder.
ln -sf $AVAILABLE_PATH/paint_domain.conf $ENABLED_PATH/paint_domain.conf
ln -sf $AVAILABLE_PATH/paint_domain-le-ssl.conf $ENABLED_PATH/paint_domain-le-ssl.conf

# Start flask application.
python wsgi.py &

# Restart apache.
sudo systemctl restart apache2
