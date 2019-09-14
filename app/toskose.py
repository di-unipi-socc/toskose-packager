"""
The module where the "toskosing" process takes place.
"""

import os
import tempfile

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.common.exception import (FatalError)
from app.common.commons import (CommonErrorMessages, unpack_archive)
from app.tosca.validator import validate_csar
from app.tosca.parser import ToscaParser
from app.docker.manager import (DockerManager, ToskosingProcessType)
from app.docker.compose import generate_compose
from app.configuration.validation import ConfigValidator
from app.configuration.completer import (generate_default_config)
from app.context import build_app_context
from app.updater import toskose_model


logger = LoggingFacility.get_instance().get_logger()


class Toskoserizator:
    def __init__(self,
                 docker_url=None,
                 debug=False,
                 quiet=False):

        self._docker_url = docker_url
        self._docker_manager = DockerManager(docker_url)

        Toskoserizator.setup_logging(debug=debug, quiet=quiet)

    @property
    def docker_url(self):
        """ Returns the URL for connecting to the Docker Engine. """

        return self._docker_url

    @docker_url.setter
    def docker_url(self, docker_url):
        """ Set the URL for connecting to the Docker Engine.

        Args:
            docker_url (str): The Docker Engine URL.
        """

        self._docker_url = docker_url

    @staticmethod
    def setup_logging(debug, quiet):

        if quiet:
            LoggingFacility.get_instance().quiet()

        if debug:  # override quiet
            LoggingFacility.get_instance().debug()

    @staticmethod
    def _generate_output_path(output_path=None):
        """ Generate a default output path for toskose results. """

        if output_path is None:
            output_path = os.path.join(
                os.getcwd(),
                constants.DEFAULT_OUTPUT_PATH)

        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        except OSError as err:
            logger.error('Failed to create {0} directory'.format(output_path))
            logger.exception(err)
            raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

        logger.info('Output dir {0} built'.format(output_path))
        return output_path

    def toskosed(self, csar_path,
                 config_path=None, output_path=None, enable_push=False):
        """
        Entrypoint for the "toskoserization" process.

        Args:
            csar_path (str): The path to the TOSCA CSAR archive.
            config_path (str): The path to the Toskose configuration file.
            output_path (str): The path to the output directory.
            enable_push (bool): Enable/Disable the auto-pushing of toskosed
                images to Docker Registries.
        Returns:
            The docker-compose file representing the TOSCA-based application.
        """

        if not os.path.exists(csar_path):
            raise ValueError('The CSAR file {} doesn\'t exists'.format(
                csar_path))
        if config_path is not None:
            if not os.path.exists(config_path):
                raise ValueError(
                    'The configuration file {} doesn\'t exists'.format(
                        config_path))
        if output_path is None:
            logger.info('No output path detected. \
                A default output path will be generated.')
            output_path = Toskoserizator._generate_output_path()
        if not os.path.exists(output_path):
            raise ValueError('The output path {} doesn\'t exists'.format(
                output_path))

        csar_metadata = validate_csar(csar_path)

        # temporary dir for unpacking data from .CSAR archive
        # temporary dir for building docker images
        with tempfile.TemporaryDirectory() as tmp_dir_context:
            with tempfile.TemporaryDirectory() as tmp_dir_csar:
                try:
                    unpack_archive(csar_path, tmp_dir_csar)
                    manifest_path = os.path.join(
                        tmp_dir_csar,
                        csar_metadata['Entry-Definitions'])

                    model = ToscaParser().build_model(manifest_path)

                    if config_path is None:
                        config_path = generate_default_config(model)
                    else:
                        ConfigValidator().validate_config(
                            config_path,
                            tosca_model=model)

                        # try to auto-complete config (if necessary)
                        config_path = generate_default_config(
                            model,
                            config_path=config_path)

                    toskose_model(model, config_path)
                    build_app_context(tmp_dir_context, model)

                    for container in model.containers:
                        if container.is_manager:
                            logger.info('Detected [{}] node [manager].'.format(
                                container.name))
                            template = ToskosingProcessType.TOSKOSE_MANAGER
                        elif container.hosted:
                            # if the container hosts sw components
                            # then it need to be toskosed
                            logger.info('Detected [{}] node.'.format(
                                container.name))
                            template = ToskosingProcessType.TOSKOSE_UNIT
                        else:
                            # the container doesn't host any sw component,
                            # left untouched
                            continue

                        ctx_path = os.path.join(
                            tmp_dir_context,
                            model.name,
                            container.name)

                        self._docker_manager.toskose_image(
                            src_image=container.image.name,
                            src_tag=container.image.tag,
                            dst_image=container.toskosed_image.name,
                            dst_tag=container.toskosed_image.tag,
                            context=ctx_path,
                            process_type=template,
                            app_name=model.name,
                            toskose_image=container.toskosed_image.base_name,
                            toskose_tag=container.toskosed_image.base_tag,
                            enable_push=enable_push
                        )

                    generate_compose(
                        tosca_model=model,
                        output_path=output_path,
                    )

                    self.quit()

                except Exception as err:
                    logger.error(err)
                    raise FatalError(
                        CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def quit(self):
        self._docker_manager.close()
