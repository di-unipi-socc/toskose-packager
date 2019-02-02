import os
import sys
from pathlib import Path
import unittest
import logging
import logging.handlers as handlers

from flask import Flask
from flask_bcrypt import Bcrypt

from config import AppConfig
from config import configs

from core.logging import LoggingFacility
from core.toskose_manager import ToskoseManager


basedir = os.path.abspath(os.path.dirname(__file__))

bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__)

    """ dynamically load configuration based on mode (prod, dev, test) """
    app.config.from_object(configs[AppConfig._APP_MODE])

    """ init flask extensions """
    bcrypt.init_app(app)

    """ register blueprints """
    from tosca import bp as bp_tosca_api
    app.register_blueprint(bp_tosca_api)

    if not app.debug and not app.testing:

        """ remove default handler and add our custom handler """
        from flask.logging import default_handler
        app.logger.removeHandler(default_handler)

        app.logger.addHandler(LoggingFacility.__call__().get_handler())
        app.logger.setLevel(logging.INFO)
        app.logger.info('- Toskose Manager API started -')

    return app


if __name__ == "__main__":

    """ Logging """
    LoggingFacility()

    """ Load App Configuration

    ToskoseManager is initialized for the first time here, then it can be
    used overall the application environment by calling the singleton instance
    from the class.
    """
    ToskoseManager.get_instance().load()

    """ Create the Flask Application with the application factory"""
    flask_app = create_app()

    flask_app.app_context().push()
    flask_app.run()
