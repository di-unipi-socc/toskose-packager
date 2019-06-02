"""
Toskose - A tool for translating a TOSCA application into docker-compose.
"""
__name__ = 'toskose'
__author__ = 'Matteo Bogo'
__email__ = 'matteo.bogo@protonmail.com'
__license__ = 'MIT'
__version__ = '0.1.0'

class ExitStatus:
    SUCCESS = 0
    ERROR = 1
    PLUGIN_ERROR = 7
    ERROR_CTRL_C = 130
    ERROR_TIMEOUT = 2
    ERROR_TOO_MANY_REDIRECTS = 6
    ERROR_HTTP_3XX = 3
    ERROR_HTTP_4XX = 4
    ERROR_HTTP_5XX = 5