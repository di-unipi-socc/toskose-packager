#!/bin/bash

echo "Configure virtualenv and flask environment.."
source venv/bin/activate
export FLASK_APP=app/run.py
export FLASK_ENV=development
echo "Configure database.."
flask db init
flask db migrate -m "user table"
flask db upgrade
echo "List of available endpoints.."
flask routes
echo "Starting the development server.."
flask run
