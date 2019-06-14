import pytest

import os
import tempfile
from configparser import ConfigParser

import tests.helpers as helpers
import tests.commons as commons

from app.supervisord.configurator import build_config, DEFAULT_CONFIG_NAME


# indirect parametrization of the fixture in conftest.py
@pytest.mark.parametrize('model', commons.apps_data, indirect=True)
class TestSupervisordConfigGeneration:

    # https://docs.pytest.org/en/latest/unittest.html#using-autouse-fixtures-and-accessing-other-fixtures
    @pytest.fixture(autouse=True)
    def initializer(self, model, context):
        """ Autoinvoked fixture for initializing test class """
        self._model = model
        self._context = context
        self._manager = None
        self._classic_containers = []
        for container in self._model.containers:
            if container.is_manager:
                self._manager = container
            else:
                self._classic_containers.append(container)
    
    def test_unit_supervisord_config_generation(self):
        """ Test the Supervisord config generation for classic containers """

        for container in self._classic_containers:
            node_context = os.path.join(
                self._context, container.name)
            
            build_config(container, node_context)
            
            assert os.path.exists(
                os.path.join(
                    node_context,
                    DEFAULT_CONFIG_NAME))

    def test_wrong_context_path(self):
        with pytest.raises(ValueError):
            build_config(self._manager, 'abcdefg')

    @pytest.mark.xfail(
        raises=StopIteration, 
        reason='the tosca app doesn\'t have a standalone container')
    def test_standalone_container_without_cmd(self):

        standalone_container = next(c for c in self._classic_containers if not c.hosted)
        standalone_container.cmd = None
        node_context = os.path.join(self._context, standalone_container.name)
        with pytest.raises(ValueError):
            build_config(standalone_container, node_context)
        


# @pytest.mark.parametrize('model', commons.apps_data, indirect=True)
# def test_supervisord_conf_generation(model, context):

#     for container in model.containers:
#         template = SupervisordTemplateType.Unit
#         if container.is_manager:
#             template = SupervisordTemplateType.Manager

#         node_dir = os.path.join(context, container.name)
#         build_config(
#             template
#             tosca_model=model,
#             container=container,
#             output_dir=node_dir)
    
#         config = ConfigParser()
#         config.read(os.path.join(node_dir, 'supervisord.conf'))

#         assert set(commons.supervisord_config_common_sections) \
#             .issubset(set(config.sections()))

#         for k,v in data['supervisord'][container.name].items():
#             section = 'program:{}'.format(k)
#             assert config.has_section(section)
#             assert config.get(section, 'command') == v['command']
#             assert config.get(section, 'stdout_logfile') == v['stdout_logfile']
