import os
import sys


basedir = os.path.abspath(os.path.dirname(__file__))


class FlaskConfig(object):
    """ Flask Configuration """

    SECRET_KEY = os.environ.get('SECRET_KEY') or \
        'to-iterate-is-human-to-recurse-divine'
    DEBUG = False

    # Logging
    TOSKOSE_LOGS_PATH = os.environ.get('TOSKOSE_LOG_PATH') or None

    # Toskose Manager Configuration
    TOSKOSE_MANAGER_CONFIG_PATH = \
        os.environ.get('TOSKOSE_MANAGER_CONFIG_PATH') or \
            os.path.join(basedir, 'resources', 'toskose.conf')


class DevelopmentConfig(FlaskConfig):
    DEBUG = True


class TestingConfig(FlaskConfig):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class ProductionConfig(FlaskConfig):
    DEBUG = False


configs = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
