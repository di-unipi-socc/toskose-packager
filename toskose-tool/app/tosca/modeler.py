import os
from dataclasses import dataclass, field
from typing import List, Dict
from toscaparser.tosca_template import ToscaTemplate

from app.common.logging import LoggingFacility
from app.common.exception import ToscaParsingError


logger = LoggingFacility.get_instance().get_logger()


# TODO dynamic types
# make some logic to obtain dynamically the list of types,
# including derived types (e.g. APISoftware is derived from
# tosker.nodes.Software), consider also tosker-types.yml

class ToscaTypes(object):
    pass

class ToscaNodeTypes(ToscaTypes): # WILL BE DEPRECATED
    SOFTWARE = 'tosker.nodes.Software'
    CONTAINER = 'tosker.nodes.Container'
    VOLUME = 'tosker.nodes.Volume'
    
class ToscaArtifactTypes(ToscaTypes):
    IMAGE = 'tosker.artifacts.Image'

@dataclass
class Artifact:
    name: str
    path: str

@dataclass
class Input:
    key: str
    value: str

@dataclass
class Interface:
    """ Represents a lifecycle operation """
    name: str
    implementation: str         # script path
    envs: List[Input]           # envs vars

@dataclass
class Component:
    name: str
    artifacts: List[Artifact]
    interfaces: List[Interface]

@dataclass
class Container:
    name: str
    image: str
    image_repository: str
    ports: List[str]
    components: List[Component]
    def add_component(self, component):
        self.components.append(component)

@dataclass
class ToscaModel:
    name: str
    containers: List[Container]

class TPLManager:
    """ """
    
    def __init__(self, tpl):
        self._tpl = tpl

    # TODO (?)
    
class ToscaModeler:
    """ """

    def __init__(self, manifest_path):
        self._manifest_path = manifest_path
        self._model = None
        
    @property
    def manifest_path(self):
        return self._manifest_path

    @property
    def model(self):
        return self._model

    def build(self):
        """ """

        try:

            app_name, ext = os.path.splitext(
                os.path.basename(self._manifest_path))

            tosca = ToscaTemplate(self._manifest_path)

            repositories = tosca.tpl.get('repositories')
            if not repositories:
                pass
                # raise error? cannot fetch images

            topology_template = tosca.tpl.get('topology_template')
            if not topology_template:
                pass
                # raise error? cannot fetch node templates

            node_templates = topology_template.get('node_templates')
            if not node_templates:
                pass
                # raise error? cannot fetch nodes

            containers = []

            # FIRST LOOP - initialize containers
            for node_key, node_value in node_templates.items():
                node_type = node_value.get('type')
                if node_type == ToscaNodeTypes.CONTAINER:
                    
                    # properties
                    container_ports = []
                    container_properties = node_value.get('properties')
                    if container_properties:

                        ## properties - ports
                        for port_key, port_value in container_properties.get('ports').items():
                            container_ports.append(port_key)

                    # artifacts
                    image_name = None
                    image_repository = None
                    container_artifacts = node_value.get('artifacts')
                    if container_artifacts:

                        ## artifacts - image
                        image_name = (container_artifacts.get('my_image')).get('file')
                        image_repository = repositories.get(
                            container_artifacts['my_image']['repository'],
                            None
                        )

                        ## TODO other artifacts?

                    #TODO requirements (?)

                    containers.append(Container(
                        node_key,
                        image_name,
                        image_repository,
                        container_ports,
                        []
                    ))

            # SECOND LOOP - searching for components
            for node_key, node_value in node_templates.items():
                node_type = node_value.get('type')
                # WILL BE DEPRECATED: 'APISoftware' with a list of derived types from
                # tosker.nodes.Software, etc..
                if node_type == ToscaNodeTypes.SOFTWARE or node_type == 'APISoftware':
                    
                    # artifacts
                    sw_artifacts_list = []
                    sw_artifacts = node_value.get('artifacts')
                    if sw_artifacts:
                        for artifact_name, artifact_path in sw_artifacts.items():
                            sw_artifacts_list.append(Artifact(
                                artifact_name,
                                artifact_path
                            ))

                    # requirements
                    host_name = None
                    sw_requirements = node_value.get('requirements')
                    if sw_requirements:

                        ## requirements - host (container) - required? # TODO rewrite?
                        for entry in sw_requirements:
                            if 'host' in entry:
                                host_name = entry.get('host')

                        ## TODO requirements - connection(s) ?

                    # interfaces
                    sw_interfaces_std_list = []
                    sw_interfaces = node_value.get('interfaces')
                    if sw_interfaces:

                        ## interfaces - Standard
                        sw_interfaces_std = sw_interfaces.get('Standard')
                        for std_name, std_value in sw_interfaces_std.items():

                            ### interfaces - Standard - inputs
                            sw_interfaces_std_inputs_list = []
                            sw_interfaces_std_inputs = std_value.get('inputs')
                            if sw_interfaces_std_inputs:

                                for std_input_name, std_input_value in sw_interfaces_std_inputs.items():
                                    sw_interfaces_std_inputs_list.append(Input(
                                        std_input_name,
                                        std_input_value
                                    ))


                            sw_interfaces_std_list.append(Interface(
                                std_name,
                                std_value.get('implementation'),
                                sw_interfaces_std_inputs_list
                            ))

                        ## interfaces - Derivated #TODO WILL BE DEPRECATED
                        # with derived interfaces list
                        sw_interfaces_derived_list = []
                        sw_interfaces_derived = sw_interfaces.get('api_interface')
                        if sw_interfaces_derived:
                            for derived_name, derived_value in sw_interfaces_derived.items():
                                sw_interfaces_derived_list.append(Interface(
                                    derived_name,
                                    derived_value['implementation'],
                                    [
                                        Input('data', 'artifacts/default_data.csv'),
                                        Input('port', '8080')
                                    ]
                                ))
                        sw_interfaces_std_list.extend(sw_interfaces_derived_list)
                        # NOTE: we need a tpl handler to manage { get_artifact: [ SELF, default_data ]}
                        # the code above need to be re-writed well (now it is just for testing)
                
                    component = Component(
                        node_key, 
                        sw_artifacts_list,
                        sw_interfaces_std_list
                    )

                    # insert the component in the right container based on the host requirement
                    for container in containers:
                        if container.name == host_name:
                            container.add_component(component)
                            break        

            self._model = ToscaModel(app_name, containers)

        except ValueError as err:
            logger.exception(err)
            raise ToscaParsingError('Failed building the TOSCA model')
