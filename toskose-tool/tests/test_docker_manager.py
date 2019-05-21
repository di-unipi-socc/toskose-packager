import pytest

import os
import pprint
import tempfile

from docker import DockerClient
from docker.errors import ImageNotFound

import app.docker.manager # used for mock inputs
import unittest.mock as mock

from app.docker.manager import DockerManager
from app.common.exception import DockerOperationError
from app.common.exception import DockerAuthenticationFailedError
from app.common.exception import OperationAbortedByUser
from app.common.exception import FatalError


src_image = 'stephenreed/jenkins-java8-maven-git'
dst_image = 'test/thinking-maven-toskosed'
wrong_toskose_image = 'diunipisocc/toskosee-unit'
dst_tag = '1.2-beta'
src_tag = wrong_toskose_tag = 'latest'

context_path = os.path.join(
    os.path.dirname(__file__), 
    'resources/thinking/node-1')

@pytest.yield_fixture
def dit():
    """
    This code will initialize the manager obj before tests start.
    The obj is yielded and then it's injected as an argument to tests.
    Finally the manager obj is gracefully closed.
    """
    dit = DockerManager()
    yield dit
    dit.close()    


def test_image_name_generation_default():
    """ Test the Docker Image name generation routine. """

    user_input = [
        '',         # repository (default: Docker Hub)
        'user',     # user (required)
        '',         # image name (default: tosca container node name)
        '',         # tag (default: latest)
    ]

    with mock.patch('builtins.input', side_effect=user_input):
        assert DockerManager.generate_image_name('node-name') == \
            'user/node-name:latest'


def test_image_name_generation_abort():
    """ Test the Docker Image name generation routine aborted by the user. """
    
    # abort user input
    user_input = ['','0']
    with pytest.raises(OperationAbortedByUser):
        with mock.patch('builtins.input', side_effect=user_input):
            DockerManager.generate_image_name('node-name')


@pytest.mark.parametrize(
    'user_input',
    [
        ['test','admin','test-image','1.0.1'],
        ['test1', 'user', 'test-image', '2.1.1'],
    ]
)
def test_image_name_generation_param(user_input):
    """ Test the Docker Image generation routine with multiple inputs. """
    
    with mock.patch('builtins.input', side_effect=user_input):
        assert DockerManager.generate_image_name('node-name') == \
            '{0}/{1}/{2}:{3}'.format(*user_input) # unpack args


def test_image_auth_not_correct(dit):
    """ Test the authentication subroutine for private repos pull aborted by the user. """
    
    with pytest.raises(OperationAbortedByUser):
        with mock.patch('builtins.input', return_value='NO'):
            dit._image_authentication(
                src_image,
                src_tag
            )


def test_image_auth_max_attempts(dit):
    """ Test the authentication subroutine for private repos pull with max attempts reached (auth failure). """
    
    src_image='asdasdsdsdsdasas'
    logins = [('a','1'), ('b','2'), ('c','3'), ('d','4')]
    with pytest.raises(DockerAuthenticationFailedError):
        with mock.patch('builtins.input', return_value='YES'):
            for login in logins:
                with mock.patch('getpass.getuser', return_value=login[0]):
                    with mock.patch('getpass.getpass', return_value=login[1]): 
                        dit._image_authentication(
                            src_image,
                            src_tag
                        )


# def test_image_auth(dit):
    """ Test the authentication subroutine for private repos pull with successfully authentication. """

#     src_image = 'insert-private-repository'
#     src_tag = 'insert-tag'
#     login = ('insert-user-here', 'insert-password-here')
#     with mock.patch('builtins.input', return_value='YES'):
#         with mock.patch('getpass.getuser', return_value=login[0]):
#             with mock.patch('getpass.getpass', return_value=login[1]):
#                 dit._image_authentication(
#                     src_image,
#                     src_tag
#                 )


def test_toskose_unit_wrong(dit):
    """ Test the "toskose" image process with a wrong toskose-unit Docker Image. """

    with pytest.raises(DockerOperationError):
        dit.toskose_image(
            src_image,
            dst_image,
            context_path,
            toskose_image=wrong_toskose_image
        )


def test_toskose_image(dit):
    """ Test the "toskose" image process without pushing the generated image. """
    
    #dit._verbose = True
    dit.toskose_image(
        src_image,
        dst_image,
        context_path,
        src_tag=src_tag,
        dst_tag=dst_tag,
        enable_push=False
    )
    
    full_name = dst_image + ':' + dst_tag
    dc = DockerClient(base_url=None)
    
    img = dc.images.get(dst_image)
    assert full_name in img.tags

    
def test_auth_push_fail_attempts(dit):
    """ Test the "toskose" image process with authentication max attempts reached during a push to a private repo. """

    logins = [('a','1'), ('b','2'), ('c','3'), ('d','4')]
    with pytest.raises(FatalError):
        for login in logins:
           with mock.patch('getpass.getuser', return_value=login[0]):
                with mock.patch('getpass.getpass', return_value=login[1]): 
                    dit.toskose_image(
                        src_image,
                        dst_image,
                        context_path,
                        src_tag=src_tag,
                        dst_tag=dst_tag
                    )


# def test_auth(dit):
    """ Test the "toskose" image process with a successfully authentication during the push of the generated image. """

#     with mock.patch('getpass.getuser', return_value='enter-username-here'):
#         with mock.patch('getpass.getpass', return_value='enter-password-here'):
#             # (e.g. test/test-image:1.0)
#             dst_image = 'enter-private-test-repository:tag'
#             dit.toskose_image(
#                 src_image,
#                 dst_image,
#                 context_path
#             )