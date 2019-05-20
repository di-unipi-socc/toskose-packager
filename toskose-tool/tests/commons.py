import tests.helpers as helpers


supervisord_config_common_sections = [
    'inet_http_server',
    'supervisord',
    'rpcinterface:supervisor',
]

apps_data = [
    {
        'manifest_path': helpers.full_path('thinking-app/thinking.csar'),
        'name': 'thinking',
        'containers': ['maven','node', 'mongodb'],
        'software': ['api', 'gui'],
        'volumes': ['dbvolume'],
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