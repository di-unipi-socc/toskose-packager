APP_REPOSITORY = 'https://github.com/matteobogo/toskose'

# DOCKER
TOSKOSE_UNIT_IMAGE = 'diunipisocc/toskose-unit'
TOSKOSE_UNIT_TAG = 'latest'
TOSKOSE_MANAGER_IMAGE = 'diunipisocc/toskose-manager'
TOSKOSE_MANAGER_TAG = 'latest'

DEFAULT_TOSKOSE_MANAGER_NAME = 'toskose-manager'

DOCKER_IMAGE_REQUIRED_DATA = [
    'repository',
    'user',
    'password',
    'name',
    'tag'
]

# SUPERVISORD
DEFAULT_SUPERVISORD_HTTP_PORT = 9001

DEFAULT_SUPERVISORD_HTTP_USER = 'admin'
DEFAULT_SUPERVISORD_HTTP_PASSWORD = 'admin'
DEFAULT_SUPERVISORD_LOG_LEVEL = 'info'

DEFAULT_SUPERVISORD_ENVS = {
    'http_port': None,
    'http_user': DEFAULT_SUPERVISORD_HTTP_USER,
    'http_password': DEFAULT_SUPERVISORD_HTTP_PASSWORD,
    'log_level': DEFAULT_SUPERVISORD_LOG_LEVEL
}

# MANAGER
TOSKOSE_MANAGER_REQUIRED_DATA = {
    'http_port': 10000,
    'http_user': 'admin',
    'http_password': 'admin',
}

# EXTRA
DEFAULT_OUTPUT_PATH = 'toskose_out'

# TOSKOSE CONFIG
DEFAULT_TOSKOSE_CONFIG_FILENAME = 'toskose.yml'