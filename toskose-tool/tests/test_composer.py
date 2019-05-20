import pytest

import tempfile
import os
import shutil

import tests.helpers as helpers
import tests.commons as commons

from app.common.commons import unpack_archive
from app.toskose import Toskoserizator
from app.docker.compose import generate_compose
from app.tosca.parser import ToscaParser


@pytest.mark.parametrize('data', commons.apps_data)
def test_compose_generation(data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also unpack the csar archive
            data['manifest_path'])

        tp = ToscaParser(manifest_path)
        tp.build()

        Toskoserizator._build_app_context(
            manifest_path, 
            commons.output_tmp_path, 
            tp.model)

        # toskosing images process - skipped

        generate_compose(tp.model, commons.output_tmp_path)
        