import tests.helpers as helpers


supervisord_config_common_sections = [
    'inet_http_server',
    'supervisord',
    'rpcinterface:supervisor',
]

apps_data = [
    # {
    #     'base_dir': helpers.full_path('sockshop'),
    #     'csar_path': helpers.full_path('sockshop/sockshop.csar'),
    #     'toskose_config': helpers.full_path(
    #         'sockshop/configurations/sockshop-toskose.yml'),
    # },
    {
        'base_dir': helpers.full_path('thinking-app'),
        'csar_path': helpers.full_path('thinking-app/thinking.csar'),
        'toskose_config': helpers.full_path(
            'thinking-app/configurations/toskose.yml'),
        'uncompleted_toskose_config': helpers.full_path(
            'thinking-app/configurations/uncompleted_toskose.yml'),
        'invalid_toskose_config': helpers.full_path(
            'thinking-app/configurations/invalid_toskose.yml'),
        'missing_node_toskose_config': helpers.full_path(
            'thinking-app/configurations/missing_node_toskose.yml'),
        'missing_docker_toskose_config': helpers.full_path(
            'thinking-app/configurations/missing_docker_toskose.yml'),
        'name': 'thinking',
        'containers': ['maven','node', 'mongodb'],
        'software': ['api', 'gui'],
        'volumes': ['dbvolume'],
        'toskose_config_manager_input': {
            'hostname': 'manager',
            'port': 10001,
            'user': 'admin',
            'password': 'admin',
            'mode': 'production',
            'secret_key': 'secret',
            'docker': {
                'name': 'thinking-manager',
                'tag': '1.0',
                'registry_password': None
            }
        },
        'toskose_config_input': {
            'maven': {
                'hostname': 'maven',
                'port': 9001,
                'user': 'admin',
                'password': 'admin',
                'log_level': 'INFO',
                'docker': {
                    'name': 'test/maven-toskosed',
                    'tag': '1.0',
                    'registry_password': None,
                },
            },
            'node': {
                'hostname': 'node',
                'port': 9002,
                'user': 'admin',
                'password': 'admin',
                'log_level': 'INFO',
                'docker': {
                    'name': 'test/node-toskosed',
                    'tag': '0.4.2',
                    'registry_password': None,
                },
            },
            'mongodb': {
                'hostname': 'mongodb',
                'port': 9003,
                'user': 'admin',
                'password': 'admin',
                'log_level': 'INFO',
                'docker': {
                    'name': 'test/mongodb-toskosed',
                    'tag': '2.1.1',
                    'registry_password': None,
                },
            },
        },
        'supervisord': {
            'maven': {
                'api-create': {
                    'command': '/bin/sh -c \'/toskose/apps/api/scripts/install.sh\'',
                    'stdout_logfile': '/toskose/apps/api/logs/api-create.log'
                },
                'api-configure': {
                    'command': '/bin/sh -c \'/toskose/apps/api/scripts/configure.sh\'',
                    'stdout_logfile': '/toskose/apps/api/logs/api-configure.log'
                },
                'api-start': {
                    'command': '/bin/sh -c \'/toskose/apps/api/scripts/start.sh\'',
                    'stdout_logfile': '/toskose/apps/api/logs/api-start.log'
                },
                'api-stop': {
                    'command': '/bin/sh -c \'/toskose/apps/api/scripts/stop.sh\'',
                    'stdout_logfile': '/toskose/apps/api/logs/api-stop.log'
                },
                'api-delete': {
                    'command': '/bin/sh -c \'/toskose/apps/api/scripts/uninstall.sh\'',
                    'stdout_logfile': '/toskose/apps/api/logs/api-delete.log'
                },
                'api-push_default': {
                    'command': '/bin/sh -c \'/toskose/apps/api/scripts/push_default.sh\'',
                    'stdout_logfile': '/toskose/apps/api/logs/api-push_default.log'
                }
            },
            'node': {
                'gui-create': {
                    'command': '/bin/sh -c \'/toskose/apps/gui/scripts/install.sh\'',
                    'stdout_logfile': '/toskose/apps/gui/logs/gui-create.log'
                },
                'gui-configure': {
                    'command': '/bin/sh -c \'/toskose/apps/gui/scripts/configure.sh\'',
                    'stdout_logfile': '/toskose/apps/gui/logs/gui-configure.log'
                },
                'gui-start': {
                    'command': '/bin/sh -c \'/toskose/apps/gui/scripts/start.sh\'',
                    'stdout_logfile': '/toskose/apps/gui/logs/gui-start.log'
                },
                'gui-stop': {
                    'command': '/bin/sh -c \'/toskose/apps/gui/scripts/stop.sh\'',
                    'stdout_logfile': '/toskose/apps/gui/logs/gui-stop.log'
                },
                'gui-delete': {
                    'command': '/bin/sh -c \'/toskose/apps/gui/scripts/uninstall.sh\'',
                    'stdout_logfile': '/toskose/apps/gui/logs/gui-delete.log'
                }
            },
            'mongodb': { }
        }
    }
]
output_tmp_path = '/tmp/toskose_test/'
supervisord_envs = [
    'SUPERVISORD_HTTP_PORT',
    'SUPERVISORD_HTTP_USER',
    'SUPERVISORD_HTTP_PASSWORD',
    'SUPERVISORD_LOG_LEVEL'
]
toskose_manager_envs = [
    'HTTP_PORT',
    'HTTP_USER',
    'HTTP_PASSWORD'
]