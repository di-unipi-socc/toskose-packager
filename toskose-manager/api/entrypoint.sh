gunicorn --bind 0.0.0.0:${TOSKOSE_MANAGER_PORT} 'app.run:create_app()'
