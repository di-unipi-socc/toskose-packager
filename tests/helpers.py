import os

from app.common.commons import unpack_archive
from app.tosca.validator import validate_csar

def full_path(path):
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'data/{}'.format(path))

def compute_manifest_path(tmp_dir, archive_path):
    csar_metadata = validate_csar(archive_path)
    unpack_archive(archive_path, tmp_dir)
    return os.path.join(tmp_dir, csar_metadata['Entry-Definitions'])