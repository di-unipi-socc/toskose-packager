import pytest

import tempfile
import os
import shutil

import tests.helpers as helpers
import tests.commons as commons

from app.common.commons import unpack_archive
from app.docker.compose import generate_compose
from app.tosca.parser import ToscaParser
from app.context import build_app_context
from app.toskose import Toskoserizator
from app.loader import Loader


@pytest.mark.parametrize('data', commons.apps_data)
def test_compose_generation(data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.TemporaryDirectory() as ctx_dir:
            manifest_path = helpers.compute_manifest_path(
                tmp_dir,    # also unpack the csar archive
                data['csar_path'])

            model = ToscaParser().build_model(manifest_path)
            tsk = Toskoserizator()

            config_path = tsk._generate_default_config(
                model, 
                uncompleted_config=data['toskose_config'],
            )

            tsk._toskose_model(model, config_path)
            build_app_context(ctx_dir, model)

            # toskosing images process - skipped
            
            if not os.path.exists(commons.output_tmp_path):
                os.makedirs(commons.output_tmp_path)
            
            generate_compose(model, commons.output_tmp_path)
        