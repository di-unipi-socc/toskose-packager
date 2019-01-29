import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'to-iterate-is-human-to-recurse-divine'
    DEBUG = False

    # Logging
    TOSKOSE_LOGS_PATH = os.environ.get('TOSKOSE_LOG_PATH') or None


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True


class ProductionConfig(Config):
    DEBUG = False


configs = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)
