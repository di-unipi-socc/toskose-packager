import pytest

import os

import tests.commons as commons
from app.tosca.validator import validate_csar


base_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data')

csars = [
    os.path.join(base_path, 'thinking-app/thinking.csar')
]


@pytest.mark.parametrize('data', commons.apps_data)
def test_validate_tosca_manifest(data):

    try:
        csar_metadata = validate_csar(data['csar_path'])
        print(csar_metadata)
        assert csar_metadata['Entry-Definitions'] == 'thinking.yaml'
    except Exception as err:
        print(err)
        assert False
