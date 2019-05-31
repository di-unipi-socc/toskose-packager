import pytest

import os
import tempfile

import tests.helpers as helpers
import tests.commons as commons

from app.toskose import Toskoserizator
from app.toskose import ToscaParser
from app.context import build_app_context
from app.configurator import Loader
from app.docker.manager import ToskosingProcessType


@pytest.fixture
def model_fixture():
    def _parser(manifest_path):
        return ToscaParser().build_model(manifest_path)
    return _parser


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_images(model_fixture, data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.TemporaryDirectory() as tmp_ctx:
            model = model_fixture(
                helpers.compute_manifest_path(
                    tmp_dir,    # also un pack the csar archive
                    data['csar_path']))

            t = Toskoserizator()
            t._toskose_model(model, data['toskose_config'])
            build_app_context(tmp_ctx, model)

            for container in model.containers:
                
                template = \
                ToskosingProcessType.TOSKOSE_MANAGER if container.is_manager \
                    else ToskosingProcessType.TOSKOSE_UNIT

                ctx_path = os.path.join(tmp_ctx, model.name, container.name)
                
                t._docker_manager.toskose_image(
                    container.image.name,
                    container.image.tag,
                    container.toskosed_image.name,
                    container.toskosed_image.tag,
                    ctx_path,
                    template,
                    enable_push=False
                )


@pytest.fixture()
def tsk():
    return Toskoserizator()

@pytest.mark.parametrize('data', commons.apps_data)
def test_toskoserizator(tsk, data):
    tsk.toskosed(
        data['csar_path'],
        data['toskose_config'],
        enable_push=False
    )