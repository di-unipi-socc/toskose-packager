import os

import pytest

import tests.commons as commons
from app.supervisord.configurator import DEFAULT_CONFIG_NAME, build_config


# indirect parametrization of the fixture in conftest.py
@pytest.mark.parametrize('configs', commons.apps_data, indirect=True)
class TestSupervisordConfigGeneration:

    # https://docs.pytest.org/en/latest/unittest.html#using-autouse-fixtures-and-accessing-other-fixtures
    @pytest.fixture(autouse=True)
    def initializer(self, model, tmpdir):
        """ Autoinvoked fixture for initializing test class """

        root_dir = tmpdir.mkdir('supervisord_configs')

        self._model = model
        self._manager = None
        self._classic_containers = []
        for container in self._model.containers:
            if container.is_manager:
                self._manager = container
            else:
                self._classic_containers.append(container)
                root_dir.mkdir(container.name)

        self._context = root_dir

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
