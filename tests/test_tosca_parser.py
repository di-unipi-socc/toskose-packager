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
def test_tosca_parser(data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)

        assert model.name == data['name']
        assert set([x.name for x in model.containers]) == set(data['containers'])
        assert set([x.name for x in model.software]) == set(data['software'])
        assert set([x.name for x in model.volumes]) == set(data['volumes'])

        # TODO test relationships
        # TODO test artifacts


@pytest.mark.parametrize('data', commons.apps_data)
def test_toskose_model(data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['csar_path'])

        model = ToscaParser().build_model(manifest_path)

        config = Loader().load(data['toskose_config'])

        tsk = Toskoserizator()
        tsk._toskose_model(model, data['toskose_config'])

        # test if the model is updated with toskose-related data
        for container in model.containers:

            if container.name == constants.DEFAULT_MANAGER_NAME:
                pass
            else:
                supervisord_data = config['nodes'][container.name]
                
                if container.hosted:
                    for k,v in supervisord_data.items():
                        if k != 'docker':
                            rev_key = 'SUPERVISORD_{}'.format(k.upper())
                            if rev_key in container.env:
                                assert v == container.env[rev_key]
                            else:
                                assert False

                assert isinstance(container.toskosed_image, ToskosedImage)

                docker_data = config['nodes'][container.name]['docker']
                for k,v in docker_data.items():
                    v = str(v) if v is not None else v
                    assert getattr(container.toskosed_image, k) == v


def test_tosca_functions_resolution_thinking():
    with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = helpers.compute_manifest_path(
                tmp_dir,    # also un pack the csar archive
                commons.apps_data[0]['csar_path'])

            tosca = ToscaTemplate(manifest_path)
            base_path = '/'.join(tosca.path.split('/')[:-1])

            # test resolution of function 'get_input' : 'gui_port' for node "maven"
            # in the tosca template related section
            maven_node_original = {
				'ports': {
					8080: {
						'get_input': 'api_port'
					}
				}
			}

            maven_node_updated = {
				'ports': {
					8080: 8000
				}
			}

            old_tpl = copy.deepcopy(tosca)
            assert old_tpl.topology_template.tpl['node_templates']['maven']['properties'] == maven_node_original

            ToscaParser._parse_functions(tosca, {}, base_path)
            assert tosca.topology_template.tpl['node_templates']['maven']['properties'] == maven_node_updated

            
@pytest.fixture
def model_fixture():
    def _parser(manifest_path):
        return ToscaParser().build_model(manifest_path)
    return _parser


@pytest.mark.parametrize('data', commons.apps_data)
def test_build_app_context(model_fixture, data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.TemporaryDirectory() as tmp_ctx:
            model = model_fixture(
                helpers.compute_manifest_path(
                    tmp_dir,    # also un pack the csar archive
                    data['csar_path']))

            tks = Toskoserizator()
            tks._toskose_model(model, data['toskose_config'])
            build_app_context(tmp_ctx, model)
        
            # check paths
            root_dir = os.path.join(tmp_ctx, model.name)
            assert os.path.exists(root_dir)
            manager_path = os.path.join(root_dir, constants.DEFAULT_MANAGER_NAME)
            assert os.path.exists(manager_path)

            #TODO test dirs structure


@pytest.mark.parametrize('data', commons.apps_data)
def test_context_app_thinking(data):
    """ Generate the context's app in a temporary dir. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.TemporaryDirectory() as ctx_dir:
            if os.path.exists(commons.output_tmp_path):
                shutil.rmtree(commons.output_tmp_path, ignore_errors=True)
            os.makedirs(os.path.join(commons.output_tmp_path))
            
            manifest_path = helpers.compute_manifest_path(
                tmp_dir,    # also un pack the csar archive 
                data['csar_path'])

            model = ToscaParser().build_model(manifest_path)
            tks = Toskoserizator()

            build_app_context(ctx_dir, model)