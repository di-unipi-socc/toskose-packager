import os
import pytest
import zipfile
import tempfile

from app.tosca.modeler import ToscaModeler
from app.common.commons import unpack_archive
from app.toskoserizator import Toskoserizator

def test_tosca_modeler():

    csar_path = '/home/matteo/git/toskose/tests/data/thinking-app/thinking.csar'
    csar_unpacked_path = '/home/matteo/git/toskose/tests/data/thinking-app/thinking'
    output_path = '/home/matteo/temp/bbb'

    #with tempfile.TemporaryDirectory() as tmp_dir:
    try:
        #unpack_archive(csar_path, tmp_dir)
        #manifest_path = os.path.join(tmp_dir, 'thinking.yaml')

        manifest_path = os.path.join(csar_unpacked_path, 'thinking.yaml')

        tm = ToscaModeler(manifest_path)
        tm.build()
        #print(tm.model.__dict__)

        Toskoserizator.build_app_context(
            csar_unpacked_path, 
            output_path, 
            tm.model
        )
        
    except Exception as err:
        print(err)
        assert False
