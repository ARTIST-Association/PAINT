#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv

# Activate virtual environment.
source $ENV_PATH/bin/activate

# Navigate to html directory.
cd ${PAINT_ROOT}/html || exit 1

# Kill flask application.
kill $(ps aux | grep '[p]ython wsgi.py' | awk '{print $2}')

# Start flask application.
python wsgi.py &

# Restart apache.
sudo systemctl restart apache2
