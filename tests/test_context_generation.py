import os
import copy
import pytest

import tests.commons as commons
from app.context import build_app_context
from app.common.exception import FatalError, AppContextGenerationError
from app.tosca.model.artifacts import File
from app.toskose import Toskoserizator

@pytest.mark.parametrize('configs', commons.apps_data, indirect=True)
class TestContextGeneration:

    @pytest.fixture(autouse=True)
    def initializer(self, model, tmpdir):
        self._model = model
        self._context = tmpdir.mkdir('app_context')

    def test_build_app_context(self):
        """ Test the generation of the app context """
        
        build_app_context(self._context, self._model)
        root_dir = os.path.join(self._context, self._model.name)
        for container in self._model.containers:
            if container.is_manager:
                # manager
                pass
            elif not container.hosted:
                # standalone
                pass
            else:
                # classic
                container_dir = os.path.join(root_dir, container.name)
                assert os.path.exists(container_dir)
                assert os.path.isfile(os.path.join(container_dir, 'supervisord.conf'))
                for software in container.hosted:
                    software_dir = os.path.join(container_dir, software.name)
                    assert os.path.exists(software_dir)
                    
                    artifacts_dir = os.path.join(software_dir, 'artifacts')
                    assert os.path.exists(artifacts_dir)
                    for artifact in software.artifacts:
                        fname = artifact.file
                        artifact_path = os.path.join(artifacts_dir, fname)
                        assert os.path.isfile(artifact_path)
                    
                    logs_dir = os.path.join(software_dir, 'logs')
                    assert os.path.exists(os.path.join(logs_dir))
                    assert os.path.isfile(os.path.join(logs_dir, '{}.log'.format(software.name)))

                    scripts_dir = os.path.join(software_dir, 'scripts')
                    assert os.path.exists(scripts_dir)
                    scripts = list()
                    for k,v in software.interfaces.items():
                        for sub_k, sub_v in v.items():
                            operation = sub_v['cmd']
                            if isinstance(operation, File):
                                operation = operation.file
                            scripts.append(operation)
                    for script in scripts:
                        script_path = os.path.join(scripts_dir, script)
                        assert os.path.isfile(script_path)

    def test_build_app_wrong_context(self):
        with pytest.raises(ValueError):
            build_app_context('abcde', self._model)

    def test_build_app_wrong_model(self):
        with pytest.raises(TypeError):
            build_app_context(self._context, None)