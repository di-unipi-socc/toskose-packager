import pytest
import os
from toscaparser.tosca_template import ToscaTemplate
from app.tosca.loader import ToscaLoader

csars = [
        '/home/matteo/git/toskose/tests/data/thinking-app/thinking.csar'
]

@pytest.mark.parametrize("file_path",csars)
def test_tosca_template(file_path):

    try:
        tl = ToscaLoader(file_path)

        print(tl.get_paths)
        print(tl.csar_metadata)

        assert tl.archive_path == '/home/matteo/git/toskose/tests/data/thinking-app/thinking.csar'
        assert tl.manifest_file == 'thinking.yaml'

        manifest = os.path.join(tl.csar_dir_path, tl._manifest_file)
        tt = ToscaTemplate(manifest)

        # verify template
        tt.verify_template()

        has_nested = tt.has_nested_templates()
        tpl = tt.tpl

        print(tpl)

        
    except Exception as err:
        pytest.fail('Unexpected Error: {0}'.format(err))
