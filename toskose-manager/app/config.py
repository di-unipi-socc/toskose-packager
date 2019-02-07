import os
import sys


class AppConfig(object):

    _CLIENT_PROTOCOL = os.environ.get('TOSKOSE_CLIENT_PROTOCOL', default='XMLRPC')

    _LOGS_CONFIG_NAME = 'logging.conf'
    _LOGS_PATH = os.environ.get('TOSKOSE_LOGS_PATH')

    _APP_CONFIG_NAME = 'toskose.toml'
    _APP_CONFIG_PATH = os.environ.get('TOSKOSE_APP_CONFIG_PATH')
    _APP_MODE = os.environ.get('TOSKOSE_APP_MODE', default='development')

    _APP_VERSION = os.environ.get('TOSKOSE_APP_VERSION')

class FlaskConfig(object):
    """ Flask Base Configuration

    SECRET_KEY: used to sign cookies and other things (**important)
    DEBUG: activate the debugging mode (e.g. unhandled exceptions, reloading
    server when code changes). It is overridden by FLASK_DEBUG env.
    ERROR_404_HELP: disable the automagically hint on 404 response messages
    """

    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        default='to-iterate-is-human-to-recurse-divine')
    DEBUG = False
    TESTING = False
    ERROR_404_HELP = False


class DevelopmentConfig(FlaskConfig):
    """ Flask Development Configuration """

    DEBUG = True


class TestingConfig(FlaskConfig):
    """ Flask Testing Configuration """

    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class ProductionConfig(FlaskConfig):
    pass

configs = dict(
    development=DevelopmentConfig,
    testing=TestingConfig,
    production=ProductionConfig
)
