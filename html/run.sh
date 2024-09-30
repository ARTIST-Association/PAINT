#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv

# Activate virtual environment.
source $ENV_PATH/bin/activate

# Navigate to html directory.
cd ${PAINT_ROOT}/html || exit 1

# Start flask application.
python wsgi.py &
