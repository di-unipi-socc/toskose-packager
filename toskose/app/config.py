class AppConfig(object):
    """ Application Configuration """

    _LOGS_CONFIG_NAME = 'logging.conf'
    _LOGS_PATH = os.environ.get('TOSKOSE_LOGS_PATH')

    _APP_NAME = 'Toskose'
    _APP_MODE = os.environ.get('TOSKOSE_APP_MODE', default='development')
    _APP_VERSION = os.environ.get('TOSKOSE_APP_VERSION')