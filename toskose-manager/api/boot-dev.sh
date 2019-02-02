#!/bin/bash

#echo "Configure virtualenv and flask environment.."
#source venv/bin/activate
#export FLASK_APP=app/run.py
#export FLASK_ENV=development
#echo "List of available endpoints.."
#flask routes
#echo "Starting the development server.."
#flask run

source venv/bin/activate
export FLASK_ENV=development
export TOSKOSE_APP_MODE=development
python3 app/run.py run
