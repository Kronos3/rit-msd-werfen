#!/bin/bash

export PATH="$PATH:/home/pi/.local/bin"
export DISPLAY=:0

cd /home/pi/git/msd-gem-5000/src
uvicorn web.main:app --host 0.0.0.0 --port 8000