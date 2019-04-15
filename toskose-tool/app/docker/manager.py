from docker import DockerClient
from docker.errors import APIError

from app.common.logging import LoggingFacility
from app.common.exception import DockerOperationError


logger = LoggingFacility.get_instance().get_logger()


class DockerManager():

    def __init__(self, base_url):
        
        self._client = DockerClient(base_url)
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

    

    def close(self):
        """ close the session """
        self._client.close()
    

    

