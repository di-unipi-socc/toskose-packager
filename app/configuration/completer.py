"""
The module for auto-completing Toskose's configuration.
"""

import os
import copy

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.loader import Loader

logger = LoggingFacility.get_instance().get_logger()


def generate_image_name_interactive(autocomplete_data=None):
    """ Generate a full name [repository]/<user>/<name><:tag>
    for a Docker Image interactively.

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
    #         registry_password = getpass.getpass(
    #               prompt='Enter the password \
    #                   for repository authentication: ')

    return {
        'name': full_name,
        'tag': tag,
        'registry_password': registry_password,
    }


def generate_default_config(tosca_model, config_path=None, output_path=None):
    """ Generate a default toskose YAML configuration
    and dump it in a directory.

    Args:
        tosca_model (object): The model of a TOSCA-based application.
        config_path: A path containing a toskose configuration.
        output_path (str): The path in which the generated configuration
            will be dumped.
    """

    def _autocomplete_config(config, name, is_manager=False):

        port = constants.gen_default_port()

        if is_manager:
            defaults = copy.deepcopy(constants.DEFAULT_MANAGER_API)
        else:
            defaults = copy.deepcopy(constants.DEFAULT_NODE_API)

        for key, default_value in defaults.items():
            if key not in config:
                logger.info('Missing field [{0}] in node [{1}] \
                    (auto-generated)'.format(
                    key,
                    name))

            value = config.get(key, default_value)

            # note: special case defaults are generated dynamically according
            # to the tosca model data and they cannot be store as fixed
            # defaults
            if not is_manager:

                # special case (auto-generation of port)
                # TODO fix bug: we need to check if the generated port will
                # not conflict with other user-defined ports of previous
                # containers, i.e. a user can define a port as the default
                # generated one
                if key == 'port':
                    value = next(port)

                # special case (auto-generation of network alias from the
                # container name)
                if key == 'alias':
                    value = name

            config[key] = value

        # note: no manager and no host =>
        # the node doesn't have any api configuration
        # (it will not be "toskosed"). However, it needs docker
        # data for the deployment.
        if 'docker' not in config:
            config['docker'] = {}
            logger.info('Missing [docker] field in node \
            [{}] (auto-generated)'.format(
                name))

        config.update({'docker':
                      generate_image_name_interactive(
                        autocomplete_data=config['docker'])})

    loader = Loader()
    config = dict()
    if config_path is None:
        logger.info(
            'No configuration detected. Default data will be generated.')
    else:
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                'The given toskose configuration doesn\'t exists')

        config = loader.load(config_path)
        logger.info('Detected configuration [{}].'.format(config_path))

    config_path = os.path.join(
        tosca_model.tmp_dir,
        constants.DEFAULT_TOSKOSE_CONFIG_FILENAME)
    if output_path is not None:
        config_path = output_path

    # exploiting the TOSCA model for completing missing data
    # nodes
    if 'nodes' not in config:
        logger.info('Missing [nodes] field (auto-generated)')
        config['nodes'] = dict()

    for container in tosca_model.containers:
        if not container.hosted:
            # no data in the toskose config for a standalone container.
            # skipping
            continue
        if container.name not in config['nodes'] \
                or config['nodes'][container.name] is None:
            config['nodes'][container.name] = dict()
            logger.info(
                'Missing node [{}] - [docker] data will be asked'.format(
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
        constants.DEFAULT_MANAGER_CONFIG_FIELD,
        is_manager=True)

    loader.dump(
        config,
        config_path,
        ordered=True)

    logger.info('{0} configuration stored in [{1}]'.format(
        'A default' if config_path is None else 'Given',
        config_path))

    return config_path
