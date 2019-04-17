import os
import yaml
from yaml import YAMLError
from dataclasses import dataclass
from typing import List, Dict
from app.common.logging import LoggingFacility


logger = LoggingFacility.get_instance().get_logger()

_compose_supported_versions = [ '3.3' ]
_compose_default_version = '3.3'

_base_service = {
    "image": "",
    "deploy": {
        "mode": "",
        "replicas": "",
        "restart_policy": {
            "condition": ""
        },
    },
    "environments": [],
    "networks": ['toskose-network'],
    "ports": [],
    "volumes": []
}

_base_networks = {
    "toskose-network": {
        "driver": "overlay",
        "attachable": True
    }
}

_base_template = {
    "version": "",
    "services": {},
    "networks": _base_networks,
    "volumes": {}
}

class DockerComposeGenerator:
    """ """

    def __init__(self, version=None):
        if version is None or version not in _compose_supported_versions:
            self._version = _compose_default_version
        else:
            self._version = version
        logger.info('Using docker-compose v.{0}'.format(self._version))
        
        self._compose = dict(_base_template)

    def _validate(self):
        pass

    def generate(self, tosca_model, output_path, name='docker-compose'):
        """ """

        #TODO check tosca_model and output_path

        self._compose.update({"version": self._version})

        for container in tosca_model.containers:

            envs = list(map(lambda x: '{0}={1}'.format(x[0],x[1]), container.get_envs()))

            service = dict(_base_service)
            service.update({
                "image": container.image,
                "environments": envs,
                "ports": container.ports
            })

            self._compose.get('services')[container.name] = service

        # TODO volumes , networks, ...
        # TODO !!fix!! some references

        final_path = os.path.join(output_path, name)
        with open(final_path, 'w') as out:
            try:
                yaml.dump(self._compose, out)
            except YAMLError as err:
                logger.exception(err)
                #TODO custom exception
                raise

        logger.info('{0} successfully generated in {1}'.format(name, output_path))
        
@dataclass
class RestartPolicy:
    condition: str

@dataclass
class Deploy:
    mode: str
    replicas: int
    restart_policy: RestartPolicy

@dataclass
class Service:
    image_name: str
    image_repository: str
    deploy: Deploy
    environments: Dict
    command: str
    networks: List[str]
    ports: List[int]
    volumes: List[str]

@dataclass
class Network:
    name: str
    driver: str = 'overlay'
    attachable: str = 'true'

@dataclass
class Volume:
    name: str

@dataclass
class ComposeTemplate:
    services: List[Service]
    networks: List[Network]
    volumes: List[Volume]