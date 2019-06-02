APP_REPOSITORY = 'https://github.com/matteobogo/toskose'

DEFAULT_OUTPUT_PATH = 'toskose_out'

DEFAULT_TOSKOSE_CONFIG_FILENAME = 'toskose.yml'
DEFAULT_TOSKOSE_CONFIG_SCHEMA_PATH = 'config_schema.json'

# Docker Compose
DEFAULT_DOCKER_COMPOSE_FILENAME = 'docker-compose.yml'
DEFAULT_DOCKER_COMPOSE_VERSION = '3.3'

DOCKER_COMPOSE_SUPPORTED_VERSIONS = [ '3.3' ]

# Toskose Unit - default configurations
DEFAULT_SUPERVISORD_INIT_HTTP_PORT = 9000
DEFAULT_SUPERVISORD_HTTP_USER = 'admin'
DEFAULT_SUPERVISORD_HTTP_PASSWORD = 'admin'
DEFAULT_SUPERVISORD_LOG_LEVEL = 'INFO'

DEFAULT_TOSKOSE_UNIT_BASE_IMAGE = 'diunipisocc/toskose-unit'
DEFAULT_TOSKOSE_UNIT_BASE_TAG = 'latest'

DEFAULT_TOSKOSE_IMAGE_TAG = 'latest' 

_supervisord_http_port = DEFAULT_SUPERVISORD_INIT_HTTP_PORT
def _get_default_http_port():
    global _supervisord_http_port
    _supervisord_http_port += 1
    return _supervisord_http_port

def _get_default_image_name(app_name, node_name):
    return '{0}-{1}-toskosed'.format(app_name, node_name)

DEFAULT_NODE_API = {
    'http_port': _get_default_http_port(),
    'http_user': DEFAULT_SUPERVISORD_HTTP_USER,
    'http_password': DEFAULT_SUPERVISORD_HTTP_PASSWORD,
    'log_level': DEFAULT_SUPERVISORD_LOG_LEVEL,
}

DEFAULT_NODE_DOCKER = {
    'name': _get_default_image_name,
    'tag': DEFAULT_TOSKOSE_IMAGE_TAG,
    'registry_password': None,
}

DEFAULT_NODE = {
    'api': DEFAULT_NODE_API,
    'docker': DEFAULT_NODE_DOCKER,
}

# Toskose Manager - default configurations
DEFAULT_MANAGER_NAME = 'toskose-manager'
DEFAULT_MANAGER_HTTP_PORT = 10000
DEFAULT_MANAGER_USER = 'admin'
DEFAULT_MANAGER_PASSWORD = 'admin'

DEFAULT_MANAGER_LOGS_PATH = '/toskose/logs'
DEFAULT_MANAGER_APP_MODE = 'production'
DEFAULT_MANAGER_SECRET_KEY = 'secret'

DEFAULT_MANAGER_BASE_IMAGE = 'diunipisocc/toskose-manager'
DEFAULT_MANAGER_BASE_TAG = 'latest'

DEFAULT_TOSKOSE_MANAGER_VOLUME_NAME = 'toskose-manager-volume'

DEFAULT_MANAGER_API = {
    'http_port': DEFAULT_MANAGER_HTTP_PORT,
    'http_user': DEFAULT_MANAGER_USER,
    'http_password': DEFAULT_MANAGER_PASSWORD,
    'mode': DEFAULT_MANAGER_APP_MODE,
    'secret_key': DEFAULT_MANAGER_SECRET_KEY,
}

FIXED_MANAGER_API = {
    'TOSKOSE_LOGS_PATH': DEFAULT_MANAGER_LOGS_PATH
}

DEFAULT_MANAGER = {
    'api': {**FIXED_MANAGER_API, **DEFAULT_MANAGER_API},
    'docker': DEFAULT_NODE_DOCKER,
}
