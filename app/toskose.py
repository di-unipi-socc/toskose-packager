""" 
The module where the "toskosing" process takes place.
"""

import os
import copy
import tempfile
import zipfile
import shutil
import ruamel.yaml
from collections import OrderedDict

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.common.exception import FatalError
from app.common.exception import ParsingError
from app.common.exception import ValidationError
from app.common.exception import PartialValidationError
from app.common.commons import CommonErrorMessages
from app.common.commons import unpack_archive
from app.common.commons import create_input_with_dflt
from app.tosca.validator import validate_csar
from app.tosca.parser import ToscaParser
from app.docker.manager import DockerManager
from app.docker.manager import ToskosingProcessType
from app.docker.manager import generate_image_name_interactive
from app.docker.compose import generate_compose
from app.loader import Loader
from app.configuration.validation import ConfigValidator
from app.context import build_app_context
from app.tosca.model.artifacts import File, DockerImage, ToskosedImage
from app.tosca.model.relationships import HostedOn
from app.tosca.model.nodes import Container, Volume, Software


logger = LoggingFacility.get_instance().get_logger()


class Toskoserizator:
    def __init__(self, 
        docker_url=None,
        debug=False, 
        quiet=False):

        self._docker_url = docker_url
        self._docker_manager = DockerManager(docker_url)
        self._loader = Loader()
        self._validator = ConfigValidator()

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


    def _generate_default_config(self, tosca_model, uncompleted_config=None, output_path=None):
        """ Generate a default toskose YAML configuration and dump it in a directory. 
        
        Args:
            tosca_model (object): The model of a TOSCA-based application.
            uncompleted_config: A dict containing a uncompleted toskose configuration.
            output_path (str): The path in which the generated configuration will be dumped.
        """

        port = constants.gen_default_port()

        def _autocomplete_config(config, name, is_manager=False):

            if is_manager:
                defaults = copy.deepcopy(constants.DEFAULT_MANAGER_API)
                for key, default_value in defaults.items():
                    if key not in config:
                        logger.info('Missing field [{0}] in node [{1}] (auto-generated)'.format(
                            key, 
                            name))
                    config[key] = config.get(key, default_value)
            
            defaults = copy.deepcopy(constants.DEFAULT_NODE_API)
            for key, default_value in defaults.items():
                if key not in config:
                    logger.info('Missing field [{0}] in node [{1}] (auto-generated)'.format(
                        key,
                        name))
                
                    # note: special case defaults are generated dynamically according
                    # to the tosca model data and they cannot be store as fixed defaults

                    # special case (auto-generation of port)
                    # TODO fix bug: we need to check if the generated port will not conflict with
                    # other user-defined ports of previous containers, i.e. a user can define a port
                    # as the default generated one
                    if key == 'port':
                        default_value = next(port)
                        
                    # special case (auto-generation of hostname)
                    if key == 'hostname':
                        default_value = name
                
                config[key] = config.get(key, default_value)

            # note: no manager and no host => the node doesn't have any api configuration
            # (it will not be "toskosed"). However, it needs docker data for the deployment.

            if 'docker' not in config:
                config['docker'] = {}
                logger.info('Missing [docker] field in node [{}] (auto-generated)'.format(
                    name))

            config.update({ 'docker': 
                generate_image_name_interactive(
                    autocomplete_data=config['docker'])})


        config = dict()
        if uncompleted_config is not None:
            if not os.path.exists(uncompleted_config):
                raise FileNotFoundError('The given toskose configuration doesn\'t exists')
            logger.info('Partial configuration detected [{}]. Try to auto-complete.'.format(uncompleted_config))
            config = self._loader.load(uncompleted_config)
        else:
            logger.info('No configuration detected. Default data will be generated.')

        config_path = os.path.join(tosca_model.tmp_dir, constants.DEFAULT_TOSKOSE_CONFIG_FILENAME)
        if output_path is not None:  
            config_path = output_path

        # meta
        if 'title' not in config:
            config['title'] = config.get('title', 'Auto-generated configuration for {}'.format(tosca_model.name))
            logger.info('Missing [title] (auto-generated)')
        if 'description' not in config:
            config['description'] = config.get('description', 'This configuration is auto-generated by toskose.')
            logger.info('Missing [description] (auto-generated)')
        
        # nodes
        if 'nodes' not in config:
            logger.info('Missing [nodes] field (auto-generated)')
            config['nodes'] = dict()

        for container in tosca_model.containers:
            if container.name not in config['nodes'] or config['nodes'][container.name] is None:
                config['nodes'][container.name] = dict()
                logger.info('Missing node [{}] - [docker] data will be asked'.format(
                    container.name))

            _autocomplete_config(
                config['nodes'][container.name], 
                container.name)

        # toskose-manager
        if 'manager' not in config:
            config['manager'] = dict()
            logger.info('Missing [manager] field (auto-generated)')

        _autocomplete_config(
            config['manager'],
            constants.DEFAULT_MANAGER_CONFIG_FIELD ,
            is_manager=True)
        
        self._loader.dump(
            config, 
            config_path,
            ordered=True)

        msg = 'Generated a default' if uncompleted_config is None \
            else 'Auto-completed'
        logger.info('{0} configuration in [{1}]'.format(msg, config_path))

        # logger.info('{0} configuration in [{1}]\n{2}'.format(
        #     msg,
        #     config_path,
        #     '', #self._loader.load(config_path, print=True)
        # ))

        return config_path

    
    def _toskose_model(self, tosca_model, config_path):
        """
        Update the TOSCA model with toskose-related data of a given configuration.

        e.g. updated model

        container.envs = {
            ...
            SUPERVISORD_HTTP_PORT: xxx,
            SUPERVISORD_HTTP_USER: yyy,
            ...
        }
        """

        def _update_free_container(container):
            """ Update the representation of a container without hosted components.
        
            Adding a "default" lifecycle operation by manipulating ENTRYPOINT or CMD commands
            within the image to be "toskosed" (that make the image runnable).
            """
            command = self._docker_manager.search_runnable_commands(
                container.image.name, container.image.tag)
            
            container.cmd = command

        configuration = self._loader.load(config_path)
        tosca_model.toskose_config_path = config_path

        nodes_config = configuration['nodes']
        for container in tosca_model.containers:

            if not container.hosted:
                logger.debug('Detected a container node [{}] without sw components hosted on'.format(
                    container.name))
                _update_free_container(container)

            supervisord_envs = { 'SUPERVISORD_{}'.format(k.upper()): v \
                for k,v in nodes_config[container.name].items() if k != 'docker' }
            container.env = supervisord_envs if container.env is None else \
                { **container.env, **supervisord_envs }

            # note: base_image and base_tag are related to the official
            # Toskose Docker base image used in the "toskosing" process
            docker_config = nodes_config[container.name]['docker']
            docker_config['base_name'] = docker_config.get('base_name')
            docker_config['base_tag'] = docker_config.get('base_tag')
            
            # docker logic about the "toskosing" process
            container.add_artifact(
                ToskosedImage(**nodes_config[container.name]['docker']))

            container.hostname = nodes_config[container.name]['hostname']

        # toskose-manager - container
        manager = Container(name='toskose-manager', is_manager=True)

        manager_config = configuration['manager']
        
        # workaround
        # the (toskose) manager isn't "toskosed" from a given image
        # we need an "empty" Docker image artifact as source image.
        manager.add_artifact(DockerImage())

        # Toskose Docker base image
        manager_config['docker']['base_name'] = \
            manager_config['docker'].get('base_name')
        manager_config['docker']['base_tag'] = \
            manager_config['docker'].get('base_tag')
        
        # The final "toskosed" image
        manager.add_artifact(
            ToskosedImage(**manager_config['docker']))
        
        manager.add_port(
            manager_config.get('port'),
            manager_config.get('port'))

        manager.hostname = manager_config.get('hostname')
        
        # toskose-manager API required envs
        manager.env = {
            'TOSKOSE_MANAGER_PORT': manager_config['port'],
            'TOSKOSE_APP_MODE': manager_config['mode'],
            'SECRET_KEY': manager_config['secret_key']
        }
                
        tosca_model.push(manager)
        
        # toskose-manager - volume
        # TODO fix? it introduces a crash of gunicorn during the
        # toskose-manager startup?
        # https://stackoverflow.com/questions/40553521/gunicorn-does-not-find-main-module-with-docker
        #tosca_model.push(Volume(constants.DEFAULT_TOSKOSE_MANAGER_VOLUME_NAME))            

    def toskosed(self, csar_path, config_path=None, output_path=None, enable_push=False):
        """ 
        Entrypoint for the "toskoserization" process.

        Args:
            csar_path (str): The path to the TOSCA CSAR archive.
            config_path (str): The path to the Toskose configuration file.
            output_path (str): The path to the output directory.
            enable_push (bool): Enable/Disable the auto-pushing of toskosed images to Docker Registries.
        Returns:
            The docker-compose file representing the TOSCA-based application.
        """

        if not os.path.exists(csar_path):
            raise ValueError('The CSAR file {} doesn\'t exists'.format(csar_path))
        if config_path is not None:
            if not os.path.exists(config_path):
                raise ValueError('The configuration file {} doesn\'t exists'.format(config_path))
        if output_path is None:
            logger.info('No output path detected. A default output path will be generated.')
            output_path = Toskoserizator._generate_output_path()
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
                    else:
                        self._validator.validate_config(
                            self._loader.load(config_path), 
                            tosca_model=model)
                        
                        # try to auto-complete config (if necessary)
                        config_path = self._generate_default_config(
                            model, 
                            uncompleted_config=config_path)                            

                    self._toskose_model(model, config_path)

                    # The "toskosing" process
                    build_app_context(tmp_dir_context, model)
                    for container in model.containers:
                        if container.is_manager:
                            logger.info('Detected [{}] node [manager].'.format(
                                container.name))
                            template = ToskosingProcessType.TOSKOSE_MANAGER
                        # elif container.hosted:
                        else:
                            # if the container hosts sw components then it need to be toskosed
                            logger.info('Detected [{}] node.'.format(
                                container.name))
                            template = ToskosingProcessType.TOSKOSE_UNIT
                        # else:
                        #     logger.info('Detected node without SW components hosted on')
                        #     template = ToskosingProcessType.TOSKOSE_FREE

                        ctx_path = os.path.join(tmp_dir_context, model.name, container.name)
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
                    raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def quit(self):
        self._docker_manager.close()
