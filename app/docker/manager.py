""" 
The Docker Manager module for handling operations with the Docker Engine.
"""

import getpass
import json
import os
import shutil
from enum import Enum, auto
from functools import reduce

from click import command
from docker import DockerClient
from docker.errors import APIError, BuildError, ImageNotFound
from docker.models.images import Image
from requests.exceptions import HTTPError

import app.common.constants as constants
from app.common.commons import CommonErrorMessages, create_auth_interactive
from app.common.exception import (DockerAuthenticationFailedError,
                                  DockerOperationError, FatalError,
                                  OperationAbortedByUser, ValidationError)
from app.common.logging import LoggingFacility

logger = LoggingFacility.get_instance().get_logger()

DOCKERFILE_TEMPLATES_PATH = 'dockerfiles'
DOCKERFILE_TOSKOSE_UNIT_TEMPLATE = 'Dockerfile-unit'
DOCKERFILE_TOSKOSE_MANAGER_TEMPLATE = 'Dockerfile-manager'
MAX_PUSH_ATTEMPTS = 3

SUPPORTED_SHELLS = [
    '/bin/bash', '/bin/sh', '/bin/zsh', 
    '/bin/tcsh', '/bin/ksh','/bin/fish'
]

DEFAULT_SHELL = ['/bin/sh', '-c']


class ToskosingProcessType(Enum):
    TOSKOSE_UNIT = auto()
    TOSKOSE_MANAGER = auto()
    TOSKOSE_FREE = auto()


def separate_full_image_name(full_name):
    """ Separate a Docker image name in its attributes.

    e.g. repository:port/user/name:tag ==> 
    {
        'repository': 'repository:port',
        'user': user,
        'name': name,
        'tag': tag
    }   
    """

    def split_tag(name_tag):
        if ':' in name_tag:
            return tuple(splitted[2].split(':'))
        else:
            return name_tag, None

    result = dict()
    splitted = full_name.split('/')
    if len(splitted) == 3:
        # private repository
        result['repository'] = splitted[0]
        result['user'] = splitted[1]
        result['name'], result['tag'] = split_tag(splitted[2])

    elif len(splitted) == 2:
        # Docker Hub
        result['repository'] = None
        result['user'] = splitted[0]
        result['name'], result['tag'] = split_tag(splitted[1])

    else:
        raise FatalError('Cannot separate {} Docker image full name'.format(full_name))

    return result


def generate_image_name_interactive(autocomplete_data=None):
    """ Generate a full name [repository]/<user>/<name><:tag> for a Docker Image interactively.
    
    Returns: 
        full_name (str): The generated full name of the Docker Image.
        data: A dict containing data about the generated image name, 
            including Docker Registry authentication.

        e.g. 'myrepository/user/test:tag'
    """

    full_name = None
    tag = None
    registry_password = None

    if autocomplete_data is not None:
        full_name = autocomplete_data.get('name')
        tag = autocomplete_data.get('tag')
        registry_password = autocomplete_data.get('registry_password')
    
    if full_name is None:
        while not full_name:
            full_name = input('Enter the [repository/]image-name: ')

    if tag is None:
        tag = input('Enter the TAG name [ENTER for latest]: ')
        if not tag:
            logger.info('No tag was provided. "latest" will be used.')
            tag = 'latest'

    # if registry_password is None:
    #     while not registry_password:
    #         registry_password = getpass.getpass(prompt='Enter the password for repository authentication: ')

    return {
        'name': full_name,
        'tag': tag,
        'registry_password': registry_password,
    }


class DockerManager():

    def __init__(self, docker_url=None, verbose=False):        
        
        self._client = DockerClient(base_url=docker_url)
        self._docker_url = docker_url
        self._verbose = verbose

        try:
            self._client.ping()
        except APIError as err:
            logger.exception(err)
            raise DockerOperationError('Failed to connect to the Docker Engine.')
    
    def get_docker_info(self):
        """ Returns info about the local docker engine """

        try:
            return {
                'info': self._client.info(),
                'version': self._client.version(),
            }
        except APIError as err:
            logger.exception(err)
            raise DockerOperationError('Failed to retrieve the Docker Engine info')

    def search_runnable_commands(self, image, tag, pull=True):
        """ Searching for ENTRYPOINT or CMD in a given image """

        def _bind_shell(cmd_list):
            """ e.g. ["/bin/sh", "-c", "echo", "hello!"] """
            if cmd_list[0] in SUPPORTED_SHELLS:
                return cmd_list
            else:
                # add a default shell on head
                return (DEFAULT_SHELL + cmd_list)

        full_name = '{0}:{1}'.format(image, tag)

        logger.info('Analyzing the [{}] image'.format(full_name))
        image = self._pull_image_with_auth(image, tag)
        
        assert (image, Image)
        
        if image is not None:
            output = self._client.api.inspect_image(full_name)
            if not output or 'Config' not in output:
                raise FatalError('Failed to inspect {} image'.format(full_name))
            else:
                entrypoint = output['Config']['Entrypoint']
                cmd = output['Config']['Cmd']

                commands = list()
                if entrypoint and not cmd:
                    logger.debug('Detected only an ENTRYPOINT: {}'.format(entrypoint))
                    commands = _bind_shell(entrypoint)
                elif not entrypoint and cmd:
                    logger.debug('Detected only a CMD: {}'.format(cmd))
                    commands = _bind_shell(cmd)
                elif entrypoint and cmd:
                    logger.debug('Detected both ENTRYPOINT: {0} and CMD: {1}'.format(
                        entrypoint, cmd))
                    # combining entrypoint (first) with cmd
                    commands = _bind_shell(entrypoint)
                    commands += cmd
                else:
                    logger.info('the {} image is not runnable. Adding an infinite sleep'.format(full_name))
                    commands = DEFAULT_SHELL + ['sleep', 'infinity']

                # add quotes
                # [0]: /bin/bash [1]: -c
                commands[2] = "\'" + commands[2]
                commands[-1] = commands[-1] + "\'"
                
                return ' '.join(commands)
    
    def _pull_image_with_auth(self, image, tag):

        try:
            return self._client.images.pull(image, tag)
        except ImageNotFound as err:
            # it should be an authentication error  
            return self._image_authentication(image, tag)  

    def _image_authentication(self, src_image, src_tag=None, auth=None):
        """ Handling Docker authentication if the image is hosted on a private repository 
        
        Args:
            src_image (str): The original image that needs authentication for being fetched.
            src_tag (str): The tag of the image above.
        """

        if src_tag is None:
            src_tag = 'latest'
        
        logger.warning('[{0}:{1}] image may not exist or authentication is required'.format(src_image, src_tag))
        res = ''
        while res != 'YES':
            res = (input('[{0}:{1}] is correct? [Yes] Continue [No] Abort\n'.format(src_image, src_tag))).upper()
            if res == 'NO':
                logger.error(
                    'Docker image [{0}:{1}] cannot be found, the operation is aborted by the user.\n(Hint: Check the TOSCA manifest.)'\
                        .format(src_image, src_tag))
                raise OperationAbortedByUser(CommonErrorMessages._DEFAULT_OPERATION_ABORTING_ERROR_MSG)
                
        attempts = 3
        while attempts > 0:
            logger.info('Authenticate with the Docker Repository..')
            try:
                if auth is None:
                    auth = create_auth_interactive(
                        user_text='Enter the username: ', 
                        pw_text='Enter the password: '
                )
                return self._client.images.pull(
                    src_image,
                    tag=src_tag,
                    auth_config=auth
                )
                break
                
            except (APIError) as err:
                msg = str(err).upper()
                if 'UNAUTHORIZED' or 'NOT FOUND' in msg:
                    logger.info('Invalid username/password.')
                else:
                    logger.exception(err)
                    raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

            attempts -= 1
            logger.info('Authentication failed. You have [{}] more attempts.'.format(attempts))

        # Check authentication failure
        if attempts == 0:
            logger.error('You have used all the authentication attempts. Abort.')
            raise DockerAuthenticationFailedError('Authentication failed. Abort.')

    
    def _push_image(self, image, tag=None, auth=None, attempts = 0):
        """ Push an image to a remote Docker Registry.
        
        Args:
            image (str): The name of the Docker Image to be pushed.
            tag (str): An optional tag for the Docker Image (default: 'latest')
            auth: An optional Dict for the authentication.
            attempts (int): The number of unsuccessful authentication attempts.
        """

        if tag is None:
            tag = 'latest'

        if attempts == MAX_PUSH_ATTEMPTS:
            err = 'Reached max attempts for pushing [{0}] with tag [{1}]'.format(
                image, tag)
            logger.error(err)
            raise FatalError(err)

        logger.info('Pushing [{0}] with tag [{1}]'.format(image, tag))
        
        result = self._client.images.push(
            image,
            tag=tag,
            auth_config=auth, 
            stream=True, 
            decode=True
        )

        # Access Denied detection
        for line in result:
            if 'error' in line: # an error is occurred
                if 'denied' or 'unauthorized' in line['error']: # access denied
                    logger.info('Access to the repository denied. Authentication failed.')
                    auth = create_auth_interactive()
                    self._push_image(
                        image,
                        tag=tag,
                        auth=auth,
                        attempts=(attempts + 1))
                else:
                    logger.error('Unknown error during push of [{0}]: {1}'.format(
                        image, line['error']))
                    raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
        
        logger.info('Image [{0}] with tag [{1}] successfully pushed.'.format(image, tag))


    def _validate_build(self, build_logs):
        """ Validate the output of the building process.
        
        Args:
            build_logs (str): The output logs of a docker image building process.
        """

        for log in build_logs:
            if 'stream' in log and self._verbose:
                print(log['stream'])
            if 'error' in log:
                logger.error('Error building the Docker Image:\n{}'.format(log['error']))
                raise DockerOperationError('Failed to "toskosing" the Docker Image. Abort.')


    def _toskose_image_availability(self, toskose_image, toskose_tag='latest'):
        """ Check the availability of the official Docker Toskose image used
            during the "toskosing" process.

        Args:
            toskose_image (str): The official Toskose Docker image.
            toskose_tag (str): The tag of the image (default: 'latest').        
        """

        try:
            _ = self._client.images.pull(
                toskose_image, 
                tag=toskose_tag)
        except ImageNotFound:
            logger.error('Failed to retrieve the official Toskose image [{0}:{1}]. Abort'.format(
                toskose_image, toskose_tag))
            raise DockerOperationError(
                'The official Toskose image {0} not found. Try later.\nIf the problem persist, open an issue at {1}'.format(
                    toskose_image, toskose_tag))


    def _remove_previous_toskosed(self, image, tag=None):
        """ Remove previous toskosed images. 
        
        Note: docker rmi doesn't remove an image if there are multiple tags 
              referencing it.

        Args:
            image (str): The name of the Docker image.
            tag (str): The tag of the Docker Image (default: 'latest').
        """

        if tag is None:
            tag = 'latest'

        def print_well(tags):
            out = ''
            for tag in tags:
                out += '- {}\n'.format(tag)
            return out

        try:

            logger.info('Searching for previous toskosed images [{0}:{1}]'.format(
                image, tag))
            image_found = self._client.images.get(image)

            logger.debug('Image [{0}] found. It\'s referenced by the following tags:\n\n{1}'.format(
                image,
                print_well(image_found.tags)))

            full_name = '{0}:{1}'.format(image, tag)
            if full_name in image_found.tags:
                self._client.images.remove(image=full_name, force=True)
                logger.info('Removed [{0}] reference from [{1}] image'.format(
                    full_name, image))
                try:
                    image_found = self._client.images.get(image)
                    logger.debug('Image [{0}][ID: {1}] still exist'.format(
                        image, image_found.id))
                except ImageNotFound:
                    logger.info('Image [{0}][ID: {1}] doesn\'t have any references yet. Removed.'.format(
                        image, image_found.id))
        except ImageNotFound:
            logger.info('No previous image found.')

    
    def toskose_image(self, src_image, src_tag, dst_image, dst_tag, context, process_type, app_name,
                      toskose_dockerfile=None, toskose_image=None, toskose_tag=None, enable_push=True):
        """  The process of "toskosing" the component(s) of a multi-component TOSCA-defined application.
        
        The "toskosing" process consists in merging contexts (e.g. artifacts, lifecycle scripts) of TOSCA software 
        component(s) and a TOSCA container node in which they are hosted on in a new docker image.
        The TOSCA container node comes with a suggested docker image, which is "enriched" by the Toskose logic 
        fetched remotely from the official Toskose Docker image, using a template Dockerfile by means of docker
        multi-stage features. This logic permits to handle the lifecycle of multiple components within the same container.
        (More details on how this process works can be found in the template Dockerfile in dockerfiles/ directory or
        in the official Toskose GitHub repository)

        In other words, this function consists in receiving a name of an existing docker image and a path to a build context,
        then by means of the docker client, the toskose template dockerfile is built and a new fresh docker image is generated.
        The new docker image includes the content of the original image, the contexts of the TOSCA software components 
        and the logic of toskose for managing them.
        
        Args:
            src_image (str): The name of the image to be "toskosed".
            src_tag (str): The tag of the image to be "toskosed".
            dst_image (str): The name of the "toskosed" image.
            dst_tag (str): The tag of the "toskosed" image.
            context (str): The path of the application context.
            process_type (enum): The type of "toskosing" process. [unit/manager/free]
            app_name (str): The name of the TOSCA application.
            toskose_dockerfile (str): The path of the template dockerfile used in the process.
            toskose_image (str): The Docker Toskose base-image used in the "toskosing" process.
            toskose_tag (str): The tag of the Docker Toskose base-image.
            enable_push (bool): enable/disable pushing of the "toskosed" image. (default: True)
        """

        if toskose_dockerfile is not None:
            if not os.path.exists(toskose_dockerfile):
                raise ValueError('The given toskose template dockerfile {} doesn\'t exist'.format(toskose_dockerfile))

        if not app_name:
            raise ValueError('A name associated to the TOSCA application must be given')

        template_dir = os.path.join(os.path.dirname(__file__), DOCKERFILE_TEMPLATES_PATH)

        # TODO can be enanched
        if process_type == ToskosingProcessType.TOSKOSE_UNIT:
            if toskose_image is None:
                toskose_image = constants.DEFAULT_TOSKOSE_UNIT_BASE_IMAGE
            if toskose_tag is None:
                toskose_tag = constants.DEFAULT_TOSKOSE_UNIT_BASE_TAG
            if toskose_dockerfile is None:
                toskose_dockerfile = os.path.join(
                    template_dir,
                    DOCKERFILE_TOSKOSE_UNIT_TEMPLATE)
        
        elif process_type == ToskosingProcessType.TOSKOSE_MANAGER:
            if toskose_image is None:
                toskose_image = constants.DEFAULT_MANAGER_BASE_IMAGE
            if toskose_tag is None:
                toskose_tag = constants.DEFAULT_MANAGER_BASE_TAG
            if toskose_dockerfile is None:
                toskose_dockerfile = os.path.join(
                    template_dir,
                    DOCKERFILE_TOSKOSE_MANAGER_TEMPLATE)

            src_image = toskose_image
            src_tag = toskose_tag

        elif process_type == ToskosingProcessType.TOSKOSE_FREE:
            pass
        
        else:
            raise ValueError('Cannot recognize the "toskosing" process {}'.format(process_type))

        if toskose_image is not None:
            self._toskose_image_availability(toskose_image, toskose_tag)

        # Check if the original image exists and needs authentication to be fetched
        # note: docker client does not distinguish between authentication error or invalid image name (?)
        logger.info('Pulling [{0}:{1}]'.format(src_image, src_tag))
        self._pull_image_with_auth(src_image, src_tag)

        self._remove_previous_toskosed(dst_image, dst_tag)
        logger.info('Toskosing [{0}:{1}] image'.format(src_image, src_tag))
        try:
            # if process_type != ToskosingProcessType.TOSKOSE_FREE:

            # copy the template dockerfile into the context
            shutil.copy2(
                toskose_dockerfile,
                context
            )

            build_args = {
                'TOSCA_APP_NAME': '{}'.format(app_name),
                'TOSCA_SRC_IMAGE': '{0}:{1}'.format(src_image, src_tag),
                'TOSKOSE_BASE_IMG': '{0}:{1}'.format(toskose_image, toskose_tag)
            }
            image, build_logs = self._client.images.build(
                path=context,
                tag='{0}:{1}'.format(dst_image, dst_tag),
                buildargs=build_args,
                dockerfile=toskose_dockerfile,
                rm=True,    # remove intermediate containers
            )
            self._validate_build(build_logs)
            
            # else:
            #     # no toskose build - just tagging it
            #     tagged = self._client.api.tag('{0}:{1}'.format(src_image, src_tag), dst_image, dst_tag, force=True)
            #     if not tagged:
            #         logger.error('Failed to tag the image [{0}:{1}] with ID [{2}]'.format(
            #             dst_image, dst_tag, image.id))
            #     logger.info('[{0}:{1}] image successfully tagged.'.format(dst_image, dst_tag))

            # push the "toskosed" image
            if enable_push:
                self._push_image(dst_image, tag=dst_tag)
            
            logger.info('[{0}:{1}] image successfully toskosed in [{2}:{3}].'.format(
                src_image, src_tag, dst_image, dst_tag))

        except (BuildError, APIError) as err:
            logger.exception(err)
            raise DockerOperationError('Failed to build image')

    def close(self):
        self._client.close()