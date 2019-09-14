import pytest

import tests.helpers as helpers
import tests.commons as commons

from app.tosca.parser import ToscaParser


@pytest.mark.parametrize('data', commons.apps_data)
@pytest.mark.parsertest  # grouping
class TestToscaParser:

    @pytest.fixture(autouse=True)
    def initializer(self, tmpdir):
        self._context = tmpdir.mkdir('parser_results')

    def test_tosca_parser(self, data):
        manifest_path = helpers.compute_manifest_path(
            self._context,    # also unpack the csar archive
            data['csar_path'])

        ToscaParser().build_model(manifest_path)
