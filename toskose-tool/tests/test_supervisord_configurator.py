import pytest
import os
import tempfile
from configparser import ConfigParser

from app.supervisord.config.configurator import SupervisordConfigGenerator
from app.supervisord.config.configurator import SupervisordTemplateType


def test_supervisord_unit_generation():

    # TemporaryDirectory will delete itself when it is done.
    # when you leave the scope of the with, the temporary directory 
    # will be deleted. With mkdtemp, you would need to do that manually.
    with tempfile.TemporaryDirectory() as tmp_dir:

        components_data = [
            {
                'name': 'front',
                'interfaces': {
                    'configure': '/toskose/apps/front/scripts/configure.sh',
                    'install': '/toskose/apps/front/scripts/install.sh',
                    'start': '/toskose/apps/front/scripts/start.sh',
                    'stop': '/toskose/apps/front/scripts/stop.sh',
                    'uninstall': '/toskose/apps/front/scripts/uninstall.sh',
                }
            },
            {
                'name': 'api',
                'interfaces': {
                    'configure': '/toskose/apps/api/scripts/configure.sh',
                    'install': '/toskose/apps/api/scripts/install.sh',
                    'start': '/toskose/apps/api/scripts/start.sh',
                    'stop': '/toskose/apps/api/scripts/stop.sh',
                    'uninstall': '/toskose/apps/api/scripts/uninstall.sh',
                }
            }
        ]

        try:

            args = {'components_data': components_data}

            SupervisordConfigGenerator(tmp_dir, config_name='supervisord.conf') \
                .build(SupervisordTemplateType.Unit, **args)

            config = ConfigParser()
            config.read(os.path.join(tmp_dir, 'supervisord.conf'))
            
            expected_sections = [
                'inet_http_server',
                'supervisord',
                'rpcinterface:supervisor',
                'program:front-configure', 
                'program:front-install', 
                'program:front-start', 
                'program:front-stop', 
                'program:front-uninstall',
                'program:api-configure', 
                'program:api-install', 
                'program:api-start', 
                'program:api-stop', 
                'program:api-uninstall'
            ]

            assert expected_sections == config.sections()                

        except Exception as err:
            print(err)
            assert False


