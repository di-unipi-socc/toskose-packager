import pytest

import os
import tempfile

from app.common.commons import unpack_archive
from app.tosca.validator import validate_csar


base_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data')

csars = [
    os.path.join(base_path, 'thinking-app/thinking.csar')
]


@pytest.mark.parametrize("archive_path",csars)
def test_validate_tosca_manifest(archive_path):

    try:
        csar_metadata = validate_csar(archive_path)
        print(csar_metadata)
        assert csar_metadata['Entry-Definitions'] == 'thinking.yaml'
    except Exception as err:
        print(err)
        assert False
