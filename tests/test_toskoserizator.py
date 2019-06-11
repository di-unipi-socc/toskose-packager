import pytest

import os
import tempfile

import tests.helpers as helpers
import tests.commons as commons

from app.toskose import Toskoserizator
from app.toskose import ToscaParser
from app.context import build_app_context
from app.loader import Loader
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
                
                if container.is_manager:
                    template = ToskosingProcessType.TOSKOSE_MANAGER
                elif container.hosted:
                    # if the container hosts sw components then it need to be toskosed
                    template = ToskosingProcessType.TOSKOSE_UNIT
                else:
                    template = ToskosingProcessType.TOSKOSE_FREE

                ctx_path = os.path.join(tmp_ctx, model.name, container.name)
                
                t._docker_manager.toskose_image(
                    src_image=container.image.name,
                    src_tag=container.image.tag,
                    dst_image=container.toskosed_image.name,
                    dst_tag=container.toskosed_image.tag,
                    context=ctx_path,
                    process_type=template,
                    app_name=model.name,
                    # toskose_image default
                    # toskose_tag default
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