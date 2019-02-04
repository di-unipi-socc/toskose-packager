#!/bin/bash

touch /toskose/supervisor/logs/supervisord.logs
pyenv local toskose-venv
supervisord -c /toskose/supervisor/supervisord.conf -l /toskose/supervisor/logs/supervisord.logs