import pytest

import os
import tempfile
from configparser import ConfigParser

import tests.helpers as helpers
import tests.commons as commons

from app.supervisord.configurator import build_config
from app.supervisord.configurator import SupervisordTemplateType
from app.tosca.parser import ToscaParser 


@pytest.mark.parametrize('data', commons.apps_data)
def test_supervisord_unit_generation(data):

    # Note: TemporaryDirectory will delete itself when it is done.
    # when you leave the scope of the with, the temporary directory 
    # will be deleted. With mkdtemp, you would need to do that manually.
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,
            data['csar_path'])
        
        model = ToscaParser().build_model(manifest_path)

        root_dir = os.path.join(tmp_dir, model.name)
        os.makedirs(root_dir)
        for container in model.containers:
            
            node_dir = os.path.join(root_dir, container.name)
            os.makedirs(node_dir)

            build_config(SupervisordTemplateType.Unit,
                tosca_model=model,
                node_name=container.name,
                output_dir=node_dir)
        
            config = ConfigParser()
            config.read(os.path.join(node_dir, 'supervisord.conf'))

            assert set(commons.supervisord_config_common_sections) \
                .issubset(set(config.sections()))

            for k,v in data['supervisord'][container.name].items():
                section = 'program:{}'.format(k)
                assert config.has_section(section)
                assert config.get(section, 'command') == v['command']
                assert config.get(section, 'stdout_logfile') == v['stdout_logfile']
