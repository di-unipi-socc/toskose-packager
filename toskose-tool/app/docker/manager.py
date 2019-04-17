import os
import shutil
from docker import DockerClient
from docker.models.images import Image
from docker.errors import APIError
from docker.errors import BuildError
from docker.errors import ImageNotFound

from app.common.logging import LoggingFacility
from app.common.commons import CommonErrorMessages
from app.common.exception import DockerOperationError
from app.common.exception import ToscaFatalError
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
        """ """

        try:
            return {
                'info': self._client.info(),
                'version': self._client.version(),
            }
        except APIError as err:
            logger.exception(err)
            raise DockerOperationError('Failed to retrieve the Docker Engine info')

    def toskose_image(self,
        src_image,
        dst_image,
        context_path,
        toskose_unit_image=AppConfig._TOSKOSE_UNIT_IMAGE):
        """ 
        
        """

        #TODO check if toskose_unit_image is available
        #TODO check if image exists
        #TODO check if login is required to fetch image

        try:

            # Remove the image if already exist
            try:
                logger.info('Detecting previous image with same name..')
                image = self._client.images.get(dst_image)
                # image found, remove it
                self._client.images.remove(
                    image=dst_image,
                    force=True
                )
                logger.info('Previous image removed.')
            except ImageNotFound:
                logger.info('No previous image found.')

            # Dockerfile template
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
            
            # Build "toskosed" image
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
            logger.exception(err)
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def close(self):
        self._client.close()
    

    

