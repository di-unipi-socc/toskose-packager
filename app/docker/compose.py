import os
import ruamel.yaml
from ruamel.yaml.scalarstring import SingleQuotedScalarString, DoubleQuotedScalarString

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.common.commons import CommonErrorMessages
from app.common.exception import FatalError, TranslationError
from app.tosca.model.relationships import HostedOn
from app.tosca.model.artifacts import File


logger = LoggingFacility.get_instance().get_logger()


# Toskose Unit
_base_service = {
    "image": None,
    "deploy": {
        "mode": 'replicated',
        "replicas": 1,
        "restart_policy": {
            "condition": DoubleQuotedScalarString('on-failure')
        },
    },
    "networks": [DoubleQuotedScalarString('toskose-network')],
}

_base_networks = {
    "toskose-network": {
        "driver": DoubleQuotedScalarString('overlay'),  # necessary for Docker DNS
        "attachable": True
    }
}

_base_template = {
    "version": None,
    "services": {},
    "networks": _base_networks,
    "volumes": {}
}


def _validate(self):
    pass       

def _volumes_template(tosca_model):
    """ Generate the docker-compose template for the TOSCA volumes. """

    volumes = {}
    for volume in tosca_model.volumes:

        logger.debug('Translating the volume node [{0}]'.format(
            volume.name))

        volumes[volume.name] = None

        if volume.driver_opt is not None:
            volumes[volume.name] = { 
                'driver_opts': [DoubleQuotedScalarString(e) for e in volume.driver_opt] 
            }
        
        # TODO external=True|False? what if the volume is created outside compose?
        # make an option --ext-volumes to use ext. volumes (if they exist)?
        # TODO what about labels?
        # TODO what about name?
    
    return volumes


def _services_template(tosca_model):
    """ Generate the docker-compose template for the TOSCA container nodes. """

    # check port conflicts on the same host
    host_ports = set()
    
    services = {}
    for container in tosca_model.containers:

        logger.debug('Translating the container node [{0}]'.format(
            container.name))

        # generate volume section by exploiting volume nodes associated to the container node
        vols = []
        for volume in container.volume: 
            
            # volume is a tuple (e.g. ('/data/db', 'dbvolume'))
            # (<path/to/data>, <volume_name>)
            #TODO fix format of Volume
            vols.append('{0}:{1}'.format(
                volume[1].split('.')[1], 
                volume[0]))
                                                
        # check conflicts within the container
        container_ports = set()

        # container's ports mapping (container:host, inverted if compared to Docker standard)
        ports = []
        if container.ports is not None:
            for k,v in container.ports.items():
                logger.warning('Detected possible host\'s ports conflict for port [{}]' \
                    .format(k)) if k in host_ports else host_ports.add(k)
                logger.warning('Detected possible container\'s ports conflict for port [{0}] within the container node [{1}]' \
                    .format(v, container.name)) if v in container_ports else container_ports.add(v)
                ports.append("{0}:{1}/tcp".format(v,k))

        envs = None        
        if container.env is not None:
            envs = ["{0}={1}".format(k,DoubleQuotedScalarString(v)) for k,v in container.env.items()]

        # generate the docker-compose service's template
        service = dict({ 
            **_base_service, 
            **{
                "image": container.toskosed_image.full_name,
                "container_name": "{0}-{1}".format(tosca_model.name, container.name),
                "hostname": container.hostname
                } 
            })
        
        if envs:
            service['environment'] = envs
        if ports:
            service['ports'] = [DoubleQuotedScalarString(e) for e in ports]
        if vols:
            service['volumes'] = [DoubleQuotedScalarString(e) for e in vols]

        services[container.name] = service

    return services


def _dump_compose(output_path, compose):
    """ Dump the docker-compose file to the disk. """

    with open(output_path, 'w') as out:
        try:
            # disabling aliases in pyyaml
            noalias_dumper = ruamel.yaml.SafeDumper
            noalias_dumper.ignore_aliases = lambda self, data: True

            ruamel.yaml.round_trip_dump(compose, out,
                allow_unicode=False, 
                default_flow_style=False,
                explicit_start=True)

            # TODO remove anchors and aliases from YAML? (* and &)
        
        except Exception as err:
            logger.error('Failed to generate the docker-compose file: {}'.format(err))
            raise TranslationError(CommonErrorMessages._DEFAULT_TRANSLATION_ERROR_MSG)

    
def generate_compose(tosca_model, output_path, file_name=None, version=None):
    """ 
    Generate the docker-compose template.

    Args:
        tosca_model (object): The model representing the TOSCA-based application.
        output_path (str): The path where the docker-compose will be generated in.
        file_name (str): The name of the docker-compose file.
        version (str): The version of the docker-compose.
    """

    if not os.path.exists(output_path):
        raise ValueError('The output path must exists.')
    if file_name is None:
        file_name = constants.DEFAULT_DOCKER_COMPOSE_FILENAME
    if version is None:
        version = constants.DEFAULT_DOCKER_COMPOSE_VERSION
    if not version in constants.DOCKER_COMPOSE_SUPPORTED_VERSIONS:
        raise ValueError('The compose version {0} is not supported. Supported versions: {1}'.format(
            version, constants.DOCKER_COMPOSE_SUPPORTED_VERSIONS))
    
    logger.info('Generating the docker-compose v.{0} manifest for the [{1}] application'.format(
        version, tosca_model.name))

    compose = {**_base_template, **{'version': version}}
    
    compose['volumes'].update(_volumes_template(tosca_model))
    compose['services'].update(_services_template(tosca_model))

    _dump_compose(
        os.path.join(output_path, file_name),
        compose)

    logger.info('{0} successfully generated in {1}'.format(file_name, output_path))