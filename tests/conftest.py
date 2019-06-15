import os
import shutil
import tempfile

import pytest

import tests.helpers as helpers
from app.loader import Loader
from app.tosca.parser import ToscaParser
from app.toskose import Toskoserizator


# request is a default pytest's fixture (indirect parametrization)
# tmpdir is a default pytest's fixture (temporary folder)
@pytest.fixture
def configs(request, tmpdir):

    csar_path = request.param['csar_path']
    src_config_path = request.param['toskose_config']

    root_dir = tmpdir.mkdir('tosca_model')
    manifest_path = helpers.compute_manifest_path(
        root_dir,    # also unpack the csar archive
        csar_path)

    config_path = tmpdir.mkdir('toskose_config').join('toskose.yml')
    shutil.copy2(src_config_path, config_path)

    yield {
        'manifest': manifest_path, 
        'toskose_config': config_path,
    }

@pytest.fixture
def model(configs, tmpdir):
    """ Build a TOSCA model representation """

    model = ToscaParser().build_model(configs['manifest'])
    Toskoserizator()._toskose_model(model, configs['toskose_config'])

    yield model