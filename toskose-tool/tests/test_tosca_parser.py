import pytest

import os
import tempfile
import copy
import shutil

import tests.helpers as helpers
import tests.commons as commons

from toscaparser.tosca_template import ToscaTemplate
from app.tosca.parser import ToscaParser
from app.tosca.validator import validate_csar
from app.common.commons import unpack_archive
import app.toskose as toskose
from app.toskose import Toskoserizator


@pytest.mark.parametrize('data', commons.apps_data)
def test_tosca_parser(data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive
            data['manifest_path'])

        tp = ToscaParser(manifest_path)
        tp.build()

        assert tp.model.name == data['name']
        assert set([x.name for x in tp.model.containers]) == set(data['containers'])
        assert set([x.name for x in tp.model.software]) == set(data['software'])
        assert set([x.name for x in tp.model.volumes]) == set(data['volumes'])

        # TODO test relationships
        # TODO test artifacts


def test_tosca_functions_resolution_thinking():
    with tempfile.TemporaryDirectory() as tmp_dir:
            manifest_path = helpers.compute_manifest_path(
                tmp_dir,    # also un pack the csar archive
                commons.apps_data[0]['manifest_path'])

                

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
        tm = ToscaParser(manifest_path)
        tm.build()
        return tm
    return _parser


@pytest.mark.parametrize('data', commons.apps_data)
def test_build_app_context(model_fixture, data):
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.TemporaryDirectory() as tmp_ctx:
            tm = model_fixture(
                helpers.compute_manifest_path(
                    tmp_dir,    # also un pack the csar archive
                    data['manifest_path']))
            
            Toskoserizator._build_app_context(
                tm.manifest_path,
                tmp_ctx,
                tm.model
            )
        
            # check paths
            root_dir = os.path.join(tmp_ctx, tm.model.name)
            assert os.path.exists(root_dir)
            manager_path = os.path.join(root_dir, toskose._DEFAULT_TOSKOSE_MANAGER_WORKDIR)
            assert os.path.exists(manager_path)

            for container in tm.model.containers:

                # check Supervisord's envs
                for env in commons.supervisord_envs:
                    if env not in container.env:
                        assert False


@pytest.mark.parametrize('data', commons.apps_data)
def test_context_app_thinking(data):
    """ Generate the context's app in a temporary dir. """

    with tempfile.TemporaryDirectory() as tmp_dir:
        if os.path.exists(commons.output_tmp_path):
            shutil.rmtree(commons.output_tmp_path, ignore_errors=True)
        os.makedirs(os.path.join(commons.output_tmp_path))
        
        manifest_path = helpers.compute_manifest_path(
            tmp_dir,    # also un pack the csar archive 
            data['manifest_path'])

        tm = ToscaParser(manifest_path)
        tm.build()

        Toskoserizator._build_app_context(manifest_path, commons.output_tmp_path, tm.model)
