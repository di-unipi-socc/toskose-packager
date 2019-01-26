#!/bin/sh

echo "Start Toskose Manager API.."
export FLASK_APP=entrypoint.py
export FLASK_DEBUG=1
flask db init
flask db migrate -m "user table"
flask db upgrade
flask run
