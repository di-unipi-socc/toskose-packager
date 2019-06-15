import pytest

import os
import tempfile
import copy
import shutil

import unittest.mock as mock

import tests.helpers as helpers
import tests.commons as commons

from toscaparser.tosca_template import ToscaTemplate

import app.common.constants as constants
from app.tosca.parser import ToscaParser
from app.loader import Loader
from app.tosca.validator import validate_csar
from app.common.commons import unpack_archive
from app.toskose import Toskoserizator
from app.context import build_app_context
from app.tosca.model.artifacts import ToskosedImage


@pytest.mark.parametrize('data', commons.apps_data)
@pytest.mark.parsertest # grouping
class TestToscaParser:

    @pytest.fixture(autouse=True)
    def initializer(self, tmpdir):
        self._context = tmpdir.mkdir('parser_results')

    def test_tosca_parser(self, data):
        manifest_path = helpers.compute_manifest_path(
            self._context,    # also unpack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)