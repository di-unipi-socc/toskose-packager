import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_bcrypt import Bcrypt
from .config import Config, configs


bcrypt = Bcrypt()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])

    # Init
    bcrypt.init_app(app)

    # Blueprints
    from .tosca_api import bp as bp_tosca_api
    app.register_blueprint(bp_tosca_api)

    # Logging
    if not app.debug and not app.testing:

        if Config.TOSKOSE_LOGS_PATH is None:
            if not os.path.exists('logs'):
                os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/toskose-manager.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('- Toskose Manager API started -')

    return app
