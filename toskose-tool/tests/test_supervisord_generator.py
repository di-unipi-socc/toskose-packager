import pytest
import os
import tempfile
from configparser import ConfigParser

from app.supervisord.config.generator import SupervisordConfigGenerator
from app.supervisord.config.generator import SupervisordTemplateType


def test_supervisord_unit_generation():

    # TemporaryDirectory will delete itself when it is done.
    # when you leave the scope of the with, the temporary directory 
    # will be deleted. With mkdtemp, you would need to do that manually.
    #with tempfile.TemporaryDirectory() as tmp_dir:

        tmp_dir = '/home/matteo/temp/bbb'

        name = 'api'

        lifecycle = {
            'configure': '/toskose/apps/api/scripts/configure.sh',
            'install': '/toskose/apps/api/scripts/install.sh',
            'start': '/toskose/apps/api/scripts/start.sh',
            'stop': '/toskose/apps/api/scripts/stop.sh',
            'uninstall': '/toskose/apps/api/scripts/uninstall.sh',
        }

        try:

            kwargs = {'name': name, 'lifecycle_operations': lifecycle}

            SupervisordConfigGenerator(tmp_dir, config_name='supervisord.conf') \
                .build(SupervisordTemplateType.Unit, **kwargs)

            config = ConfigParser()
            config.read(os.path.join(tmp_dir, 'supervisord.conf'))
            
            expected_sections = [
                'inet_http_server',
                'supervisord',
                'rpcinterface:supervisor',
                'program:api-configure', 
                'program:api-install', 
                'program:api-start', 
                'program:api-stop', 
                'program:api-uninstall'
            ]

            assert expected_sections == config.sections()                

        except Exception as err:
            print(err)


