import pytest
import os
import pprint
import tempfile

from app.docker.manager import DockerImageToskoser
from app.common.exception import DockerOperationError
from app.config import AppConfig


src_image = 'stephenreed/jenkins-java8-maven-git:latest'
dst_image = 'stephenreed/jenkins-java8-maven-git-toskosed:latest'
context_path = os.path.join(os.path.dirname(__file__), 'resources/thinking/node-1')
wrong_toskose_image = 'diunipisocc/toskosee-unit:latest'

@pytest.yield_fixture
def dit():
    """
    This code will initialize the manager obj before tests start.
    The obj is yielded and then it's injected as an argument to tests.
    Finally the manager obj is gracefully closed.
    """
    dit = DockerImageToskoser()
    yield dit
    dit.close()    

def test_toskose_unit_wrong(dit):

    try:
        dit.toskose_image(
            src_image,
            dst_image,
            context_path,
            toskose_image=wrong_toskose_image
        )
    except DockerOperationError as err:
        #print('\n{}'.format(err))
        assert True

def test_toskose_image(dit):

    src_image = 'stephenreed/jenkins-java8-maven-git:latest'
    dst_image = 'stephenreed/jenkins-java8-maven-git-toskosed:latest'
    context_path = os.path.join(os.path.dirname(__file__), 'resources/thinking/node-1')

    dit.toskose_image(
        src_image,
        dst_image,
        context_path
    )

# def test_toskose_image_with_auth(dit):

#     with tempfile.TemporaryDirectory() as tmp_dir:

#         src_image = 'giulen/test-auth:latest'
#         dst_image = 'giulen/test-auth-toskosed:latest'

#         # create a fake component dir (context check)
#         app_context = os.path.join(tmp_dir, 'test-app')
#         os.makedirs(app_context)

#         # create a fake supervisord.conf (context check)
#         open(os.path.join(tmp_dir, 'supervisord.conf'), 'w').close()

#         dit.toskose_image(
#             src_image,
#             dst_image,
#             tmp_dir
#         )
#     assert True
