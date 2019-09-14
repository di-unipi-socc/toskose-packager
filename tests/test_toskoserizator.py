import pytest

import tests.commons as commons

from app.toskose import Toskoserizator
from app.toskose import ToscaParser


@pytest.fixture
def model_fixture():
    def _parser(manifest_path):
        return ToscaParser().build_model(manifest_path)
    return _parser


@pytest.mark.parametrize('data', commons.apps_data)
class TestToskoserizatorPipeline:

    def test_toskoserizator(self, data):
        Toskoserizator().toskosed(
            data['csar_path'],
            data['toskose_config'],
            enable_push=False
        )
