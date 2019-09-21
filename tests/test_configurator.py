import os
import shutil
import tempfile
import unittest.mock as mock
from builtins import print

import pytest

import tests.commons as commons
import tests.helpers as helpers
from app.common.exception import ValidationError
from app.configuration.completer import generate_default_config
from app.configuration.validation import ConfigValidator
from app.loader import Loader
from app.tosca.parser import ToscaParser
from app.common import constants

# @pytest.fixture
# def config():
#     def _parser(config_path):
#         cfg = Loader()
#         return cfg.load(config_path)
#     return _parser


@pytest.fixture
def reset_port():
    """ reset the port generator for Supervisor HTTP port """

    constants.port = constants.DEFAULT_SUPERVISORD_INIT_PORT


@pytest.mark.parametrize('data', commons.apps_data)
def test_config_validation(data):
    """ Test a valid toskose configuration. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)
        ConfigValidator().validate_config(
                data['toskose_config'],
                tosca_model=model)


@pytest.mark.parametrize('data', commons.apps_data)
def test_validate_uncompleted_config(data, reset_port):
    """ Test a valid but uncompleted toskose config. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)
        ConfigValidator().validate_config(
            data['uncompleted_toskose_config'],
            tosca_model=model)


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_invalid_config_thinking(data, reset_port):
    """ Test an invalid toskose config. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)
        with pytest.raises(ValidationError):
            ConfigValidator().validate_config(
                data['invalid_toskose_config'],
                tosca_model=model)


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_config_missing_node(data, reset_port):
    """ Test a toskose config with a missing node.

    Docker data about the missing node is asked to the user.
    """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)
        ConfigValidator().validate_config(
            data['missing_node_toskose_config'],
            tosca_model=model)


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_config_missing_docker_section(data, reset_port):
    """ Test an invalid toskose config with a missing docker section """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)
        with pytest.raises(ValidationError):
            ConfigValidator().validate_config(
                data['missing_docker_toskose_config'],
                tosca_model=model)


def test_schema_metadata():
    assert ConfigValidator().get_schema_metadata() == ['title', 'description']


def test_data_load_not_exist():
    with pytest.raises(ValueError):
        Loader().load('abcderfgh.yml')


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_uncompleted_config_thinking(data, reset_port):
    """ Test the auto-completation of toskose config. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)

        docker_inputs = [
            list(data['toskose_config_input']['maven']['docker'].values())
        ]

        def gen_inputs():
            for entry in docker_inputs:
                for subentry in entry:
                    yield subentry

        with mock.patch('builtins.input', side_effect=gen_inputs()):
            with mock.patch('getpass.getpass', return_value='password'):

                # make a copy of the config
                # because autocompletation will overwrite
                # the original configuration
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_path = os.path.join(tmp_dir, 'uncompleted_config.yml')
                    shutil.copy2(
                        data['uncompleted_toskose_config'],
                        tmp_path,
                    )

                    config_path = generate_default_config(
                        model,
                        config_path=tmp_path)
                    print(config_path)


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_model_config_gen(data, reset_port):
    """ Test the auto-generation of toskose config. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)

        docker_inputs = [
            list(v['docker'].values())
            for k, v in data['toskose_config_input'].items()]
        docker_manager_inputs = [
            list(data['toskose_config_manager_input']['docker'].values())]

        docker_inputs += docker_manager_inputs

        def gen_inputs():
            for entry in docker_inputs:
                for subentry in entry:
                    yield subentry

        with mock.patch('builtins.input', side_effect=gen_inputs()):
            with mock.patch('getpass.getpass', return_value='password'):
                config_path = generate_default_config(model)
                cfg = Loader()
                config = cfg.load(config_path)

                if 'nodes' not in config:
                    assert False

                test_data = {
                    'nodes': dict(data['toskose_config_input'])
                }

                assert config['nodes'] == test_data['nodes']
