# import pytest

# import os
# import pprint
# import tempfile

# from docker import DockerClient
# from docker.errors import ImageNotFound

# import app.docker.manager # used for mock inputs
# import unittest.mock as mock

# import tests.helpers as helpers
# import tests.commons as commons

# import app.common.constants as constants
# from app.docker.manager import ToskosingProcessType
# from app.docker.manager import DockerManager
# from app.docker.manager import generate_image_name_interactive
# from app.docker.manager import separate_full_image_name
# from app.common.exception import DockerOperationError
# from app.common.exception import DockerAuthenticationFailedError
# from app.common.exception import OperationAbortedByUser
# from app.common.exception import FatalError
# from app.tosca.model.artifacts import ToskosedImage


# src_image = 'stephenreed/jenkins-java8-maven-git'
# dst_image = 'test/thinking-maven-toskosed'
# wrong_toskose_image = 'diunipisocc/toskosee-unit'
# dst_tag = '1.2-beta'
# src_tag = wrong_toskose_tag = 'latest'

# context_path = os.path.join(
#     os.path.dirname(__file__), 
#     'resources/thinking/node-1')

# @pytest.yield_fixture
# def dit():
#     """
#     This code will initialize the manager obj before tests start.
#     The obj is yielded and then it's injected as an argument to tests.
#     Finally the manager obj is gracefully closed.
#     """
#     dit = DockerManager()
#     yield dit
#     dit.close()    


# @pytest.mark.parametrize('data', [
#     ['', 'user', 'image', ''],
#     ['url:port', 'user', 'image', 'tag']
# ])
# def test_image_name_interactive(data):
#     """ Test the Docker Image name generation interactively routine. """

#     with mock.patch('builtins.input', side_effect=data):
#         with mock.patch('getpass.getpass', return_value='password'):
#             image_data = generate_image_name_interactive()
#             tks_img = ToskosedImage(**image_data)

#             assert tks_img.full_name == '{0}{1}/{2}{3}'.format(
#                 data[0] + '/' if data[0] else data[0],
#                 data[1], data[2],
#                 ':' + data[3] if data[3] else data[3]
#             )

#             data.insert(2, 'password')
#             for k,v in image_data.items():
#                 if image_data[k] is None:
#                     image_data[k] = ''
            
#             assert image_data == dict(zip(
#                 constants.DOCKER_IMAGE_REQUIRED_DATA, 
#                 data))


# def test_image_name_generation_default():
#     """ Test the Docker Image name generation routine. """

#     user_input = [
#         'image',    # image name (required)
#         '',         # tag (default: latest)
#     ]
#     expected = {
#         'name': 'image',
#         'tag': 'latest',
#         'registry_password': None,
#     }

#     with mock.patch('builtins.input', side_effect=user_input):
#             generated = generate_image_name_interactive() 
#             user_input = [None if x == '' else x for x in user_input]
            
#             assert generated == expected


# def test_image_auth_not_correct(dit):
#     """ Test the authentication subroutine for private repos pull aborted by the user. """
    
#     with pytest.raises(OperationAbortedByUser):
#         with mock.patch('builtins.input', return_value='NO'):
#             dit._image_authentication(
#                 src_image,
#                 src_tag
#             )


# def test_image_auth_max_attempts(dit):
#     """ Test the authentication subroutine for private repos pull with max attempts reached (auth failure). """
    
#     src_image='sasaasasasas'
#     with pytest.raises(DockerAuthenticationFailedError):
#         with mock.patch('builtins.input', side_effect=['YES']):
#             dit._image_authentication(
#                 src_image,
#                 src_tag,
#                 auth={'username': 'user', 'password': 'password'}
#             )


# # def test_image_auth(dit):
#     """ Test the authentication subroutine for private repos pull with successfully authentication. """

# #     src_image = 'insert-private-repository'
# #     src_tag = 'insert-tag'
# #     login = ('insert-user-here', 'insert-password-here')
# #     with mock.patch('builtins.input', return_value='YES'):
# #         with mock.patch('getpass.getuser', return_value=login[0]):
# #             with mock.patch('getpass.getpass', return_value=login[1]):
# #                 dit._image_authentication(
# #                     src_image,
# #                     src_tag
# #                 )


# def test_toskose_unit_wrong(dit):
#     """ Test the "toskose" image process with a wrong toskose-unit Docker Image. """

#     with pytest.raises(DockerOperationError):
#         dit.toskose_image(
#             src_image,
#             src_tag,
#             dst_image,
#             dst_tag,
#             context_path,
#             ToskosingProcessType.TOSKOSE_UNIT,
#             toskose_image=wrong_toskose_image
#         )


# def test_toskose_image(dit):
#     """ Test the "toskose" image process without pushing the generated image. """
    
#     dit.toskose_image(
#         src_image,
#         src_tag,
#         dst_image,
#         dst_tag,
#         context_path,
#         ToskosingProcessType.TOSKOSE_UNIT,
#         enable_push=False
#     )
    
#     full_name = dst_image + ':' + dst_tag
#     dc = DockerClient(base_url=None)
    
#     img = dc.images.get(dst_image)
#     assert full_name in img.tags

    
# def test_auth_push_fail_attempts(dit):
#     """ Test the "toskose" image process with authentication max attempts reached during a push to a private repo. """

#     with pytest.raises(FatalError):
#         with mock.patch('builtins.input', return_value='user'):
#             with mock.patch('getpass.getpass', return_value='password'): 
#                 dit.toskose_image(
#                     src_image,
#                     src_tag,
#                     dst_image,
#                     dst_tag,
#                     context_path,
#                     ToskosingProcessType.TOSKOSE_UNIT
#                 )


# # def test_auth(dit):
#     """ Test the "toskose" image process with a successfully authentication during the push of the generated image. """

# #     with mock.patch('getpass.getuser', return_value='enter-username-here'):
# #         with mock.patch('getpass.getpass', return_value='enter-password-here'):
# #             # (e.g. test/test-image:1.0)
# #             dst_image = 'enter-private-test-repository:tag'
# #             dit.toskose_image(
# #                 src_image,
# #                 src_tag,  
# #                 dst_image,
# #                 dst_tag,
# #                 context_path
# #             )


# @pytest.mark.parametrize('data', [
#     {'repository': None, 'user': 'user', 'password': 'password', 'name': 'image', 'tag': None},
#     {'repository': 'myrepo:1000', 'user': 'user', 'password': 'password', 'name': 'image', 'tag': '1.0.1'}
# ])
# def test_separate_full_image_name(data):
#     tks_img = ToskosedImage(**data)
#     del data['password']
#     assert separate_full_image_name(tks_img.full_name) == data