""" 
The module where the "toskosing" process takes place.
"""

import os
import tempfile
import zipfile
import shutil
import toml
import ruamel.yaml
from collections import OrderedDict

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.common.exception import FatalError
from app.common.exception import ParsingError
from app.common.commons import CommonErrorMessages
from app.common.commons import unpack_archive
from app.common.commons import create_input_with_dflt
from app.tosca.validator import validate_csar
from app.tosca.parser import ToscaParser
from app.docker.manager import DockerManager
from app.docker.manager import ToskosingProcessType
from app.docker.manager import generate_image_name_interactive
from app.docker.compose import generate_compose
from app.configurator import Configurator
from app.context import build_app_context
from app.tosca.model.artifacts import DockerImage, ToskosedImage
from app.tosca.model.nodes import Container


logger = LoggingFacility.get_instance().get_logger()


class Toskoserizator:
    def __init__(self, 
        docker_url=None,
        debug=False, 
        quiet=False):

        self._docker_url = docker_url
        self._docker_manager = DockerManager(docker_url)
        self._configurator = Configurator()

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

        if debug: # override quiet
            LoggingFacility.get_instance().debug()


    @staticmethod
    def _generate_output_path(output_path=None):
        """ Generate a default output path for toskose results. """

        if output_path is None:
            output_path = os.path.join(os.getcwd(), constants.DEFAULT_OUTPUT_PATH)
        
        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        except OSError as err:
            logger.error('Failed to create {0} directory'.format(output_path))
            logger.exception(err)
            raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
            
        logger.info('Output dir {0} built'.format(output_path))
        return output_path


    def _generate_default_config(self, tosca_model):
        """ Generate a default toskose YAML configuration and dump it in a directory. 
        
        Args:
            tosca_model (object): The model of a TOSCA-based application.
        """

        logger.warn('No configuration detected. Default data will be generated.')
        default_http_port = constants.DEFAULT_SUPERVISORD_HTTP_PORT
        config_path = os.path.join(tosca_model.tmp_dir, constants.DEFAULT_TOSKOSE_CONFIG_FILENAME)
        
        config = OrderedDict(
            title='Auto-generated configuration for {}'.format(tosca_model.name),
            description='This configuration is auto-generated by toskose.',
            nodes={}
        )

        for container in tosca_model.containers:
            config['nodes'][container.name] = {}

            container_envs = dict(constants.DEFAULT_SUPERVISORD_ENVS)
            container_envs.update({'http_port': default_http_port})
            
            config['nodes'][container.name]['api'] = container_envs

            logger.info('Requesting data for [{}] node'.format(container.name))
            config['nodes'][container.name]['docker'] = generate_image_name_interactive()

        # toskose-manager
        logger.info('Requesting data for [{}] node'.format(constants.DEFAULT_TOSKOSE_MANAGER_NAME))
        config['nodes'][constants.DEFAULT_TOSKOSE_MANAGER_NAME] = dict()
        config['nodes'][constants.DEFAULT_TOSKOSE_MANAGER_NAME]['api'] = \
            dict(constants.TOSKOSE_MANAGER_REQUIRED_DATA)

        config['nodes'][constants.DEFAULT_TOSKOSE_MANAGER_NAME]['docker'] = \
            generate_image_name_interactive()
        
        config_path = os.path.join(tosca_model.tmp_dir, constants.DEFAULT_TOSKOSE_CONFIG_FILENAME)
        self._configurator.dump(
            config, 
            config_path,
            ordered=True)

        logger.info('Generated a default configuration in [{0}]\n{1}'.format(
            config_path,
            self._configurator.load(config_path, print=True)))

        return config_path

    
    def _toskose_model(self, tosca_model, config_path):
        """
        Update the TOSCA model with toskose-related data.
        If the configuration is not given, a default one is generated.

        e.g. updated model

        container.envs = {
            ...
            SUPERVISORD_HTTP_PORT: xxx,
            SUPERVISORD_HTTP_USER: yyy,
            ...
        }

        container.toskose_data: {
            ...
            DOCKER_REPOSITORY: zzz,
            DOCKER_IMAGE_NAME: www
            ...
        }
        """

        configuration = self._configurator.load(config_path)
        tosca_model.toskose_config_path = config_path

        nodes_config = configuration['nodes']
        for container in tosca_model.containers:
            
            supervisord_envs = { 'SUPERVISORD_{}'.format(k.upper()): v \
                for k,v in nodes_config[container.name]['api'].items() }
            container.env = supervisord_envs if container.env is None else \
                { **container.env, **supervisord_envs }
            
            container.add_artifact(
                ToskosedImage(**nodes_config[container.name]['docker']))

        # toskose-manager
        manager_config = nodes_config['toskose-manager']
        manager = Container(name='toskose-manager', is_manager=True)
        
        # workaround to preserve the original TosKeR DockerImage artifact
        # note: The latter doesn't consider private registries (split by ':')
        # => myprivateregistry.com:9999/user/my-image:mytag => ':' twice
        manager.image = DockerImage('') 
        manager.image.name = constants.TOSKOSE_MANAGER_IMAGE
        manager.image.tag = constants.TOSKOSE_MANAGER_TAG
        
        manager.env = { k.upper(): v for k,v in manager_config['api'].items() }
        manager.toskosed_image = ToskosedImage(**manager_config['docker'])

        tosca_model.push(manager)
                

    def toskosed(self, csar_path, config_path=None, output_path=None, enable_push=True):
        """ 
        Entrypoint for the "toskoserization" process.
        """

        if not os.path.exists(csar_path):
            raise ValueError('The CSAR file {} doesn\'t exists'.format(csar_path))
        if config_path is not None:
            if not os.path.exists(config_path):
                raise ValueError('The configuration file {} doesn\'t exists'.format(config_path))
        if output_path is None:
            output_path = Toskoserizator._generate_output_path()
            logger.debug('Using a default output path {}'.format(output_path))
        if not os.path.exists(output_path):
            raise ValueError('The output path {} doesn\'t exists'.format(output_path))

        csar_metadata = validate_csar(csar_path)

        # temporary dir for unpacking data from .CSAR archive
        # temporary dir for building docker images
        with tempfile.TemporaryDirectory() as tmp_dir_context:
            with tempfile.TemporaryDirectory() as tmp_dir_csar:
                try:
                    unpack_archive(csar_path, tmp_dir_csar)
                    manifest_path = os.path.join(tmp_dir_csar, csar_metadata['Entry-Definitions'])
                    
                    model = ToscaParser().build_model(manifest_path)

                    if config_path is None:
                        config_path = self._generate_default_config(model)

                    self._toskose_model(model, config_path)

                    # The "toskosing" process
                    build_app_context(tmp_dir_context, model)
                    for container in model.containers:

                        template = \
                            ToskosingProcessType.TOSKOSE_MANAGER if container.is_manager \
                                else ToskosingProcessType.TOSKOSE_UNIT

                        ctx_path = os.path.join(tmp_dir_context, model.name, container.name)
                        self._docker_manager.toskose_image(
                            container.image.name,
                            container.image.tag,
                            container.toskosed_image.name,
                            container.toskosed_image.tag,
                            ctx_path,
                            template,
                            enable_push=enable_push
                        )

                    generate_compose(
                        tosca_model=model,
                        output_path=output_path,
                    )

                    self.quit()
                
                except Exception as err:
                    if not isinstance(err, ParsingError):
                        logger.exception(err)
                    raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def quit(self):
        self._docker_manager.close()
