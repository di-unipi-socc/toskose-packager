APP_REPOSITORY = 'https://github.com/matteobogo/toskose'

DEFAULT_OUTPUT_PATH = 'toskose_out'

DEFAULT_TOSKOSE_CONFIG_FILENAME = 'toskose.yml'
DEFAULT_TOSKOSE_CONFIG_SCHEMA_PATH = 'config_schema.json'

# Docker Compose
DEFAULT_DOCKER_COMPOSE_FILENAME = 'docker-compose.yml'
DEFAULT_DOCKER_COMPOSE_VERSION = '3.7'

DOCKER_COMPOSE_SUPPORTED_VERSIONS = ['3.7']

# Toskose Unit - default configurations
DEFAULT_SUPERVISORD_INIT_PORT = 9000
DEFAULT_SUPERVISORD_USER = 'admin'
DEFAULT_SUPERVISORD_PASSWORD = 'admin'
DEFAULT_SUPERVISORD_LOG_LEVEL = 'INFO'

DEFAULT_TOSKOSE_UNIT_BASE_IMAGE = 'diunipisocc/toskose-unit'
DEFAULT_TOSKOSE_UNIT_BASE_TAG = 'latest'

DEFAULT_TOSKOSE_IMAGE_TAG = 'latest'

port = DEFAULT_SUPERVISORD_INIT_PORT


def gen_default_port():
    global port
    if port < 65535:
        port += 1
        yield port


def get_default_image_name(app_name, node_name):
    return '{0}-{1}-toskosed'.format(app_name, node_name)


DEFAULT_NODE_API = {
    'alias': None,
    'port': None,
    'user': DEFAULT_SUPERVISORD_USER,
    'password': DEFAULT_SUPERVISORD_PASSWORD,
    'log_level': DEFAULT_SUPERVISORD_LOG_LEVEL,
}

DEFAULT_NODE_DOCKER = {
    'name': None,
    'tag': DEFAULT_TOSKOSE_IMAGE_TAG,
    'registry_password': None,
}

DEFAULT_NODE = {
    **DEFAULT_NODE_API,
    **{'docker': DEFAULT_NODE_DOCKER},
}

# Toskose Manager - default configurations
DEFAULT_MANAGER_NAME = 'toskose-manager'
DEFAULT_MANAGER_CONFIG_FIELD = 'manager'
DEFAULT_MANAGER_ALIAS = 'toskose-manager'
DEFAULT_MANAGER_PORT = 10000
DEFAULT_MANAGER_USER = 'admin'
DEFAULT_MANAGER_PASSWORD = 'admin'

DEFAULT_MANAGER_APP_MODE = 'production'
DEFAULT_MANAGER_SECRET_KEY = 'secret'

DEFAULT_MANAGER_BASE_IMAGE = 'diunipisocc/toskose-manager'
DEFAULT_MANAGER_BASE_TAG = 'latest'

DEFAULT_TOSKOSE_MANAGER_VOLUME_NAME = 'toskose-manager-volume'

DEFAULT_MANAGER_CONFIG_DIR = 'config/'
DEFAULT_MANAGER_MANIFEST_DIR = 'manifest/'
DEFAULT_MANAGER_IMPORTS_DIR = 'imports/'

DEFAULT_MANAGER_API = {
    'alias': DEFAULT_MANAGER_ALIAS,
    'port': DEFAULT_MANAGER_PORT,
    'user': DEFAULT_MANAGER_USER,
    'password': DEFAULT_MANAGER_PASSWORD,
    'mode': DEFAULT_MANAGER_APP_MODE,
    'secret_key': DEFAULT_MANAGER_SECRET_KEY,
}

DEFAULT_MANAGER = {
    **DEFAULT_MANAGER_API,
    **{'docker': DEFAULT_NODE_DOCKER},
}
