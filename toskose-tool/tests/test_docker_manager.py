import pytest

import os
import pprint
import tempfile

from docker import DockerClient
from docker.errors import ImageNotFound

import app.docker.manager # used for mock inputs
import unittest.mock as mock

from app.docker.manager import DockerImageManager
from app.common.exception import DockerOperationError
from app.common.exception import OperationAbortedByUser
from app.common.exception import ToscaFatalError
from app.config import AppConfig


src_image = 'stephenreed/jenkins-java8-maven-git:latest'
dst_image = 'test/thinking-maven-toskosed:latest'
context_path = os.path.join(
    os.path.dirname(__file__), 
    'resources/thinking/node-1')
wrong_toskose_image = 'diunipisocc/toskosee-unit:latest'

@pytest.yield_fixture
def dit():
    """
    This code will initialize the manager obj before tests start.
    The obj is yielded and then it's injected as an argument to tests.
    Finally the manager obj is gracefully closed.
    """
    dit = DockerImageManager()
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
        assert False
    except DockerOperationError as err:
        print(err)
        assert True

def test_toskose_image(dit):

    docker_url = None

    try:

        dit.toskose_image(
            src_image,
            dst_image,
            context_path,
            enable_push=False
        )

        dc = DockerClient(base_url=docker_url)
        img = dc.images.get(dst_image)

        #assert len(img.tags) == 1
        assert dst_image in img.tags

        dc.images.remove(dst_image)
        try:
            dc.images.get(dst_image)
            assert False
        except ImageNotFound:
            assert True
        
    except Exception as err:
        print(err)
        assert False

def test_image_name_generation_default():

    user_input = [
        '',         # repository (default: Docker Hub)
        'user',     # user (required)
        '',         # image name (default: tosca container node name)
        '',         # tag (default: latest)
    ]

    with mock.patch('builtins.input', side_effect=user_input):
        result = DockerImageManager.generate_image_name('node-name')
        assert result['repository'] == 'user/node-name'
        assert result['tag'] == 'latest'

def test_image_name_generation_abort():
    
    # abort user input
    user_input = ['','0']
    with pytest.raises(OperationAbortedByUser):
        with mock.patch('builtins.input', side_effect=user_input):
            DockerImageManager.generate_image_name('node-name')


@pytest.mark.parametrize(
    'user_input',
    [
        ['test','admin','test-image','1.0.1'],
        ['test1', 'user', 'test-image', '2.1.1'],
    ]
)
def test_image_name_generation_param(user_input):

    with mock.patch('builtins.input', side_effect=user_input):
        result = DockerImageManager.generate_image_name('node-name')
        assert '{0}:{1}'.format(result['repository'], result['tag']) == \
            '{0}/{1}/{2}:{3}'.format(*user_input) # unpack args
    

def test_auth_fail_attempts(dit):
    logins = [('a','1'), ('b','2'), ('c','3'), ('d','4')]
    with pytest.raises(ToscaFatalError):
        for login in logins:
           with mock.patch('getpass.getuser', return_value=login[0]):
                with mock.patch('getpass.getpass', return_value=login[1]): 
                    dit.toskose_image(
                        src_image,
                        dst_image,
                        context_path
                    )

# def test_auth(dit):

#     with mock.patch('getpass.getuser', return_value='enter-username-here'):
#         with mock.patch('getpass.getpass', return_value='enter-password-here'):

#             # (e.g. test/test-image:1.0)
#             dst_image = 'enter-private-test-repository:tag'
#             try:
#                 dit.toskose_image(
#                     src_image,
#                     dst_image,
#                     context_path
#                 )
#             except Exception as err:
#                 print(err)
#                 assert False