import pytest
import shutil

import tests.helpers as helpers
import tests.commons as commons

from app.tosca.parser import ToscaParser
from app.tosca.model.artifacts import ToskosedImage, DockerImage
from app.toskose import Toskoserizator
from app.loader import Loader


@pytest.mark.parametrize('configs', commons.apps_data, indirect=True)
class TestToskoseModel:

    @pytest.fixture(autouse=True)
    def initializer(self, configs):
        self._manifest = configs['manifest']
        self._config = configs['toskose_config']
        self._loaded_config = Loader().load(configs['toskose_config'])

    def test_toskose_model(self):

        model = ToscaParser().build_model(self._manifest)
        tsk = Toskoserizator()
        tsk._toskose_model(model, self._config)

        # test if the model is updated with toskose-related data
        nodes_config = self._loaded_config['nodes']
        for container in model.containers:

            if container.is_manager:

                node_config = self._loaded_config['manager']

                # fake base image + toskosed image
                assert container.name == 'toskose-manager'
                assert len(container.artifacts) == 2
                
                # fake base image
                assert isinstance(container.image, DockerImage)
                assert container.image.name is None
                assert container.image.tag is None
                
                # toskosed image
                assert isinstance(container.toskosed_image, ToskosedImage)
                docker_data = node_config['docker']
                for k,v in docker_data.items():
                    v = str(v) if v is not None else v
                    assert getattr(container.toskosed_image, k) == v

                # ports mapping
                assert next(iter(container.ports.values())) == node_config['port']
                assert next(iter(container.ports.keys())) == node_config['port']

                # hostname
                assert container.hostname == node_config['hostname']

                # toskose-manager envs
                manager_envs = {
                    'TOSKOSE_MANAGER_PORT': node_config['port'],
                    'TOSKOSE_APP_MODE': node_config['mode'],
                    'SECRET_KEY': node_config['secret_key']
                }
                assert container.env == manager_envs

                # no hosted software nodes
                assert not container.hosted

            else:
                node_config = nodes_config[container.name]
                
                for k,v in node_config.items():
                    if k != 'docker':
                        rev_key = 'SUPERVISORD_{}'.format(k.upper())
                        if rev_key in container.env:
                            assert v == container.env[rev_key]
                        else:
                            assert False

                assert isinstance(container.toskosed_image, ToskosedImage)

                docker_data = node_config['docker']
                for k,v in docker_data.items():
                    v = str(v) if v is not None else v
                    assert getattr(container.toskosed_image, k) == v

                # standalone
                if not container.hosted:
                    assert container.cmd is not None