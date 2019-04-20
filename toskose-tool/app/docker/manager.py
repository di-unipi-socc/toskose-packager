import os
import shutil
import getpass
from docker import DockerClient
from docker.models.images import Image
from docker.errors import APIError
from docker.errors import BuildError
from docker.errors import ImageNotFound

from app.common.logging import LoggingFacility
from app.common.commons import CommonErrorMessages
from app.common.exception import DockerOperationError
from app.common.exception import ValidationError
from app.common.exception import ToscaFatalError
from app.common.exception import OperationAbortedByUser
from app.common.exception import DockerAuthenticationFailedError
from app.config import AppConfig


logger = LoggingFacility.get_instance().get_logger()

_DOCKERFILE_TOSKOSERIZATION_PATH = 'dockerfiles'
_DOCKERFILE_TOSKOSERIZATION_NAME = 'Dockerfile-toskoserization'


class DockerImageToskoser():

    def __init__(self, base_url=None):
        
        self._client = DockerClient(base_url=base_url)
        try:
            self._client.ping()
        except APIError as err:
            logger.exception(err)
            raise DockerOperationError('Failed to connect to the Docker Engine')
    
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
    
    @staticmethod
    def validate_context(context_path):
        """ Validate the application context. 
        
        e.g. if supervisord.conf exists, if there is at least one tosca software component
        """

        if not os.listdir(context_path):
            logger.error('Invalid context: no components found')
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

        dir_files = [f for f in os.listdir(context_path) \
            if os.path.isfile(os.path.join(context_path, f))]

        if 'supervisord.conf' not in dir_files:
            logger.error('Invalid context: supervisord.conf not found')
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def _image_authentication(self, src_image):
        """ Handling Docker authentication if the image is hosted on a private repository """
        
        logger.warning('{} docker image may not exist or authentication is required'.format(src_image))
        res = ''
        while res != 'YES':
            res = (input('{} is correct? [Yes] Continue [No] Abort\n'.format(src_image))).upper()
            if res == 'NO':
                logger.error(
                    'Docker image {} cannot be found, the operation is aborted by the user.\n(Hint: Check the TOSCA manifest.)'\
                        .format(src_image))
                raise OperationAbortedByUser('Operation aborted by the user.')
                
        attempts = 3
        while attempts > 0:
            logger.info('Authenticate with the Docker Repository..')
            try:
                repository_url = input(
                    'Enter the URL of the Docker Repository ' + \
                    '(press ENTER for the Docker Hub): ')
                username = input('Enter the username: ')
                password = getpass.getpass('Enter the password: ')

                if username and password:

                    self._client.login(
                        username=username,
                        password=password,
                        registry=repository_url
                    )

                    logger.info('Successfully authenticated.')
                    
                    # Check if image really exists
                    self._client.images.pull(src_image)
                    
                    break
                
            except APIError as err:
                if 'misbehaving' in str(err):
                    logger.info('Repository {} is invalid or not working'.format(repository_url))
                elif 'Unauthorized' in str(err):
                    logger.info('Invalid username/password.')
                elif 'Not Found' in str(err):
                    logger.error('Docker image {0} cannot be fetched from repository {1}. It does not exist.'.format(
                        src_image, repository_url))
                    raise DockerOperationError('Failed to fetch the docker image {}. It does not exist.'.format(src_image))
                else:
                    logger.exception(err)
                    raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

            attempts -= 1
            logger.info('Authentication failed. You have {} more attempts.'.format(attempts))

        # Check authentication failure
        if attempts == 0:
            logger.error('The user has used all the authentication attempts.')
            raise DockerAuthenticationFailedError('Authentication failed. Abort.')
    
    def toskose_image(self,
        src_image: str,
        dst_image: str,
        context_path: str,
        toskose_image: str =AppConfig._TOSKOSE_UNIT_IMAGE,
        toskose_tag: str =AppConfig._TOSKOSE_UNIT_IMAGE_TAG):
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
            dst_image (str): The final name of the "toskosed" image.
            context_path (str): The path of the application context.
            toskose_image (str): The name of the (official) Toskose Docker image used for the process of "toskosing".
        """

        # Validate the component(s) context
        DockerImageToskoser.validate_context(context_path)

        # Check if the (official) Toskose Docker Image is available
        try:
            tks_image = self._client.images.pull(
                toskose_image, 
                tag=toskose_tag)
        except ImageNotFound:
            logger.error('Failed to retrieve the official Toskose image')
            raise DockerOperationError(
                'Official Toskose image not found. Try later.\nIf the problem persist, open an issue at {}'.format(
                    AppConfig._APP_REPOSITORY))

        # Check if the original image exists and needs authentication to be fetched
        # note: docker client does not distinguish between authentication error or invalid image name (?)
        try:
            self._client.images.pull(src_image)
        except ImageNotFound as err:
            self._image_authentication(src_image) # it should be an authentication error
                
        # Remove the image if already exist
        try:
            # Searching for previous toskosed image
            logger.info('Searching for previous toskosed images with the same name..')
            self._client.images.get(dst_image)
            
            # Image found, remove it
            self._client.images.remove(image=dst_image, force=True)   
            logger.info('Previous image removed.')
        except ImageNotFound:
            logger.info('No previous image found.')

        try:
            # Dockerfile template for "toskosing" images
            dockerfile_template_path = \
                os.path.join(
                    os.path.dirname(__file__), 
                    _DOCKERFILE_TOSKOSERIZATION_PATH,
                    _DOCKERFILE_TOSKOSERIZATION_NAME
                )

            # Copy the template dockerfile in the app's context
            # (i.e. dir containing artifacts, scripts, etc.)
            shutil.copy2(
                dockerfile_template_path,
                context_path
            )
            
            # "toskosing" the image
            logger.info('Toskosing {0} image..'.format(src_image))

            build_args = {'TOSCA_SRC_IMAGE': src_image}
            self._client.images.build(
                path=context_path,
                tag=dst_image,
                buildargs=build_args,
                dockerfile=_DOCKERFILE_TOSKOSERIZATION_NAME
            )

            logger.info('{0} successfully toskosed in {1}.'.format(
                src_image, dst_image
            ))

        except (BuildError, APIError) as err:
            logger.exception(err)
            raise DockerOperationError('Failed to build image')
        except Exception as err:
            logger.exception('Unknown Error: {0}'.format(err))
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def close(self):
        self._client.close()