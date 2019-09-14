"""
The module where the TOSCA model is updated with
Toskose configuration.
"""
from app.common.logging import LoggingFacility
from app.loader import Loader
from app.tosca.model.artifacts import (DockerImage, ToskosedImage)
from app.tosca.model.nodes import (Container)


logger = LoggingFacility.get_instance().get_logger()


def toskose_model(tosca_model, config_path):
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

    configuration = Loader().load(config_path)
    tosca_model.toskose_config_path = config_path

    nodes_config = configuration['nodes']
    for container in tosca_model.containers:

        if not container.hosted:
            logger.info('Detected a container node [{}] without sw components \
                hosted on. Skipping.'.format(
                container.name))
            # workaround: fake the toskosed image with the original one
            # will be used to complete the "image" field
            # in the final compose file
            container.add_artifact(
                ToskosedImage(container.image.name, container.image.tag))

            # use the container name (defined in the TOSCA specifications)
            # as hostname/alias
            container.hostname = container.name

            continue

        supervisord_envs = {'SUPERVISORD_{}'.format(k.upper()): v
                            for k, v in nodes_config[container.name].items()
                            if k != 'docker'}
        container.env = supervisord_envs if container.env is None else \
            {**container.env, **supervisord_envs}

        # note: base_image and base_tag are related to the official
        # Toskose Docker base image used in the "toskosing" process
        docker_config = nodes_config[container.name]['docker']
        docker_config['base_name'] = docker_config.get('base_name')
        docker_config['base_tag'] = docker_config.get('base_tag')

        # docker logic about the "toskosing" process
        container.add_artifact(
            ToskosedImage(**nodes_config[container.name]['docker']))

        container.hostname = nodes_config[container.name]['alias']

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

    manager.hostname = manager_config.get('alias')

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
    # tosca_model.push(Volume(constants.DEFAULT_TOSKOSE_MANAGER_VOLUME_NAME))
