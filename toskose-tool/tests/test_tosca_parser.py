import pytest

import os
import tempfile
import copy

from toscaparser.tosca_template import ToscaTemplate
from app.common.commons import unpack_archive
from app.tosca.parser import ToscaParser


csar_archive_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data/thinking-app/thinking.csar')


def test_tosca_parser():

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            unpack_archive(csar_archive_path, tmp_dir)
            manifest_path = os.path.join(tmp_dir, 'thinking.yaml')

            tp = ToscaParser(manifest_path)
            tp.build()
            assert True

        except Exception as err:
            print(err)
            assert False


def test_tosca_functions_resolution():

    with tempfile.TemporaryDirectory() as tmp_dir:
        try:
            unpack_archive(csar_archive_path, tmp_dir)
            manifest_path = os.path.join(tmp_dir, 'thinking.yaml')

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

        except Exception as err:
            print(err)
            assert False