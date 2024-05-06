#!/bin/bash

source /venv/bin/activate

. prestart.sh

echo "-- Starting Supportive Shade..."

python3 main.py

