"""
The parser module for TOSCA-based applications.
"""

import os
import re
from typing import List, Dict

from toscaparser.tosca_template import ToscaTemplate
from toscaparser.functions import Function
from toscaparser.common.exception import ValidationError

from app.common.commons import CommonErrorMessages
from app.common.logging import LoggingFacility
from app.common.exception import ParsingError, FatalError

from app.tosca.model.template import Template
from app.tosca.model.nodes import Container, Software, Volume
from app.tosca.model.artifacts import File
from app.tosca.model.artifacts import Dockerfile, DockerfileExecutable
from app.tosca.model.artifacts import DockerImage, DockerImageExecutable


logger = LoggingFacility.get_instance().get_logger()

_VALIDATION_ERRORS = {
    'InvalidGroupTargetException': 'Node Templates is invalid: ',
    'MissingRequiredFieldError': 'Missing required field: ',
    'InvalidTemplateVersion': 'Template version is invalid: '
}

_DOCKER_HUB_URL_DEFAULT = 'registry.hub.docker.com'


class ToscaNodeTypes(object):
    SOFTWARE = 'tosker.nodes.Software'
    CONTAINER = 'tosker.nodes.Container'
    VOLUME = 'tosker.nodes.Volume'


class ToscaNodeArtifactTypes(object):
    DOCKERFILE = 'tosker.artifacts.Dockerfile'
    DOCKERFILE_EXE = 'tosker.artifacts.Dockerfile.Service'
    IMAGE = 'tosker.artifacts.Image'
    IMAGE_EXE = 'tosker.artifacts.Image.Service'


class ToscaRequirementTypes(object):
    REL_CONNECT = 'tosca.relationships.ConnectsTo'
    REL_DEPEND = 'tosca.relationships.DependsOn'
    REL_ATTACH = 'tosca.relationships.AttachesTo'
    REL_HOST = 'tosca.relationships.HostedOn'


def get_attributes(args, nodes):
    get = nodes
    for a in args:
        get = get[a]
    return get


class ToscaParser:
    """ A parser for TOSCA-based applications. """

    def __init__(self):
        pass

    @staticmethod
    def _update_hosted_nodes(tpl):
        for container in tpl.containers:
            for sw in tpl.software:
                if sw.host_container == container:
                    container.add_hosted_node(sw)

    @staticmethod
    def _add_pointer(tpl):
        for node in tpl.nodes:
            for rel in node.relationships:
                rel.to = tpl[rel.to]

    @staticmethod
    def _add_back_links(tpl):
        for node in tpl.nodes:
            for rel in node.relationships:
                rel.to.up_requirements.append(rel)

    @staticmethod
    def _add_extension(tpl):
        """
        This function add the following extension on the template:
        - add pointer host_container pointer on software
        - add pointer on host property
        - add software links to the corrisponding container
        """

        # Add the host_container property
        for node in tpl.software:
            
            def find_container(node):
                if isinstance(node, Container):
                    return node
                elif node.host_container is not None:
                    return node.host_container
                elif node.host is None:
                    raise ValueError('Software component must have the \"host\" requirements')
                else:
                    return find_container(node.host.to)

            node.host_container = find_container(node)
            logger.debug('%s .host %s, .host_container %s',
                node, node.host.to, node.host_container)

        # Manage the case when a Software is connected
        # to a Container or a Software
        for node in tpl.software:
            for con in node._connection:
                if isinstance(con.to, Container):
                    container = con.to
                if isinstance(con.to, Software):
                    container = con.to.host_container
                logger.debug('manage connection of %s to %s', node, container)
                node.host_container.add_overlay(container, con.to.name)

        # Manage the case whene a Container is connected to a Software
        for node in tpl.containers:
            for con in node._connection:
                if isinstance(con.to, Software):
                    con.alias = con.to.name
                    con.to = con.to.host_container

    @staticmethod
    def _parse_functions(tosca_template, inputs, base_path):
        """ Parse TOSCA functions.
        
        This function walks throught the TOSCA template searching for TOSCA functions
        placeholders, then it updates the original template by resolving them.

        e.g.
        # topology_template:
        #   inputs:
        #     api_port:
        #       type: integer
        #       default: 8000
        #       description: API port
        # ...
        # node_templates:
        #   maven:
        #     ...
        #   properties:
        #     ports:
        #       8080: { get_input: api_port }   =resolved=

        Args:
            tosca_template (object): The (toscaparser) template.
            inputs (Dict): A dictionary containing TOSCA inputs.
            base_path (str): The path of the TOSCA-based application.

        """

        def get(name, value, args):
            """ Returns the result of a TOSCA function. """

            if 'SELF' == args[0]:
                args[0] = name
            return get_attributes(args[1:], nodes[args[0]][value])

        def parse_node(name, node, tosca_inputs):
            """ Parse a TOSCA node and update the node's attributes by resolving
            inputs/outputs functions.
            
            Args:
                name (str): The node name.
                node: A dict containing the attributes associated to the node.
                    (e.g. type, artifacts, requirements, interfaces, properties)
                tosca_inputs: A dict containing the inputs associated to the TOSCA
                    topology template.
            """
            for k, v in node.items():
                # function parsed by toscaparser library
                if isinstance(v, Function):
                    node[k] = v.result()
                elif isinstance(v, dict):   # otherwise
                    
                    # get_property function is found
                    if 'get_property' in v:
                        node[k] = get(name, 'properties', v['get_property'])

                    # get_artifact function is found
                    elif 'get_artifact' in v:
                        art = get(name, 'artifacts', v['get_artifact'])
                        node[k] = File(
                            None,
                            os.path.abspath(os.path.join(base_path, art)))
                        
                    # get_input function is found
                    elif 'get_input' in v:
                        if v['get_input'] in inputs:
                            node[k] = inputs[v['get_input']]
                        else:
                            node[k] = tosca_inputs[v['get_input']]['default']

                    else:
                        parse_node(name, v, tosca_inputs)

        nodes = tosca_template.topology_template.tpl['node_templates']

        tosca_inputs = None
        if 'inputs' in tosca_template.topology_template.tpl:
            tosca_inputs = tosca_template.topology_template.tpl['inputs']

        for k, v in nodes.items():
            parse_node(k, v, tosca_inputs)

        tosca_outputs = None
        if 'outputs' in tosca_template.topology_template.tpl:
            tosca_outputs = tosca_template.topology_template.tpl['outputs']
            for k, v in tosca_outputs.items():
                parse_node(k, v, tosca_inputs)

    def build_model(self, manifest_path, inputs=None):
        """ Build the model representing the TOSCA-based application. """

        if not os.path.exists(manifest_path):
            raise ValueError('The Manifest file {} doesn\'t exists'.format(manifest_path))

        if inputs is None:
            inputs = {}

        try:
            manifest_file = os.path.basename(manifest_path)
            app_name, _ = os.path.splitext(manifest_file)

            # toscaparser Model for tosca-based applications
            # (Built-in validation for node_templates and required fields)
            tosca = ToscaTemplate(manifest_path)

            # Note: tosca.path is the path to the manifest file
            base_path = '/'.join(tosca.path.split('/')[:-1])
            logger.debug('Tosca application [{0}] located in: [{1}]'.format(
                app_name, base_path))

            # Check Repositories
            repositories = tosca.tpl.get('repositories')
            if not repositories:
                logger.error('No repositories found in {}'.format(
                    manifest_file))
                raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

            # Check Topology Template
            topology_template = tosca.tpl.get('topology_template')
            if not topology_template:
                logger.error('No topology template found in {}'.format(manifest_file))
                raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

            # Resolve TOSCA functions
            ToscaParser._parse_functions(tosca, inputs, base_path)
            
            # THE model (our custom model)
            template = Template(app_name)

            if hasattr(tosca, 'description'):
                template.description = tosca.tpl.get('description')
            if hasattr(tosca, 'outputs'):
                template.outputs = tosca.outputs
            if hasattr(tosca, 'policies'):
                pass
            
            # imports (types)
            # e.g. [{'tosker': 'tosker-types.yaml'}]
            if 'imports' in tosca.tpl:
                for imp in tosca.tpl['imports']:
                    for k,v in imp.items():
                        #TODO check if it's an URL (remote file with types, DL it)
                        #assuming local file
                        template.add_import(k,os.path.join(base_path, v))
                        logger.debug('Added Import: {0}:{1}'.format(k,v))

            template.tmp_dir = os.path.dirname(os.path.abspath(manifest_path))
            template.manifest_path = manifest_path

            # Parsing Tosca Nodes
            for node in tosca.nodetemplates:
                
                nodeObj = None

                logger.debug('Parsing node [{0}] of type: [{1}]'.format(node.name, node.type))

                # Container Node
                if node.is_derived_from(ToscaNodeTypes.CONTAINER):
                    nodeObj = Container(node.name)

                    # artifacts
                    logger.debug('Collecting artifacts from node [{0}] of type [{1}]'.format(node.name, node.type))

                    artifacts = node.entity_tpl.get('artifacts')
                    if artifacts:
                        if not isinstance(artifacts, dict):
                            logger.error('Artifacts from node [{0}] of type [{1}] is invalid, only a dict is allowed.'.format(
                                node.name, node.type))
                            raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)
                        
                        for k, v in artifacts.items():
                            
                            # docker section
                            if k == 'my_image':
                                if not isinstance(v, dict):
                                    logger.error('Docker artifact from node [{0}] of type [{1}] is invalid, only a dict is allowed.'.format(
                                        node.name, node.type))
                                    raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

                                logger.debug('Parsing the Docker artifact from node [{0}] of type [{1}]'.format(node.name, node.type))
                            
                                image_name = v.get('file')
                                artifact_type = v.get('type')
                                repository = v.get('repository')

                                # check docker required fields
                                image_fields_error = None
                                if not image_name:
                                    image_fields_error = 'missing the "file" field'
                                elif not artifact_type:
                                    image_fields_error = 'missing the "type" field'
                                elif not repository:
                                    image_fields_error = 'missing the "repository" field'

                                if image_fields_error:
                                    logger.error('Failed to parse the docker artifact from node [{0}] of type [{1}]: {2}'.format(
                                        node.name, node.type, image_fields_error))
                                    raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

                                # handling the artifact
                                if artifact_type == ToscaNodeArtifactTypes.DOCKERFILE or artifact_type == ToscaNodeArtifactTypes.DOCKERFILE_EXE:
                                    raise NotImplementedError('Dockerfile as docker artifact is not supported yet')
                                
                                elif artifact_type == ToscaNodeArtifactTypes.IMAGE or artifact_type == ToscaNodeArtifactTypes.IMAGE_EXE:
                                    logger.debug('Parsing the Docker Image of the Docker artifact from node [{0}] of type [{1}]'.format(node.name, node.type))

                                    nodeObj.image = DockerImageExecutable(image_name) \
                                        if (artifact_type == ToscaNodeArtifactTypes.IMAGE_EXE) \
                                        else DockerImage(image_name)

                                    if repository:
                                        p = re.compile('(https://|http://)')
                                        repository = p.sub('', repositories[repository]).strip('/')
                                        if repository != _DOCKER_HUB_URL_DEFAULT:
                                            nodeObj.image = '/'.join([repository.strip('/'), nodeObj.image.format.strip('/')])

                                else:
                                    logger.error('Docker artifact from node [{0}] of type [{1}] has an unknown type'.format(
                                        node.name, node.type))
                                    raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

                            else:
                                logger.error('Missing the Docker section in the node [{0}] of type [{1}]'.format(
                                    node.name, node.type))
                                raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

                    # properties
                    logger.debug('Collecting properties from node [{0}] of type [{1}]'.format(node.name, node.type))

                    properties = node.entity_tpl.get('properties')
                    if properties:
                        if not isinstance(properties, dict):
                            logger.error('Properties from node [{0}] of type [{1}] is invalid, only a dict is allowed.'.format(
                                node.name, node.type))
                            raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

                        # handling properties
                        if 'env_variable' in properties:
                            nodeObj.env = properties.get('env_variable')
                        if 'command' in properties:
                            nodeObj.cmd = properties.get('command')
                        if 'ports' in properties:
                            nodeObj.ports = properties.get('ports')
                        if 'share_data' in properties:
                            nodeObj.share_data = properties.get('share_data')
                    
                # Volume Node
                elif node.is_derived_from(ToscaNodeTypes.VOLUME):
                    
                    nodeObj = Volume(node.name)

                # Software Node
                elif node.is_derived_from(ToscaNodeTypes.SOFTWARE):
                    
                    nodeObj = Software(node.name)

                    # Artifacts
                    artifacts = node.entity_tpl.get('artifacts')
                    if artifacts:
                        logger.debug('Detected artifacts in node [{0}] of type [{1}]: {2}'.format(
                            node.name, node.type, artifacts))
                        for art_name, art_path in artifacts.items():
                            nodeObj.add_artifact(File(art_name,os.path.abspath(os.path.join(base_path, art_path))))
                            logger.debug('Added new artifact for node [{0}] of type [{1}]. Current artifacts: {2}'.format(
                                node.name, node.type, nodeObj.artifacts))

                    # Interfaces
                    interfaces = node.entity_tpl.get('interfaces')
                    if interfaces:
                        logger.debug('Detected interfaces in node [{0}] of type [{1}]: {2}'.format(
                            node.name, node.type, interfaces))
                        parsed_interfaces = {}
                        for name, interface in interfaces.items():
                            parsed_interfaces[name] = parsed_interface = {}
                            for k,v in interface.items():
                                parsed_interface[k] = operation = {}
                                if 'implementation' in v:
                                    abs_path = os.path.abspath(os.path.join(base_path, v['implementation']))
                                    operation['cmd'] = File(None, abs_path)
                                    logger.debug('Detected an implementation. Path: {0} - File: {1}'.format(
                                        operation['cmd'].path, operation['cmd'].file))
                                if 'inputs' in v:
                                    operation['inputs'] = v['inputs']
                                    logger.debug('Detected Inputs: {}'.format(
                                        { k: (v.file_path if isinstance(v, File) else v) for k, v in operation['inputs'].items()}))

                        nodeObj.interfaces = parsed_interfaces
                    
                else:
                    logger.error('Node type {} not supported'.format(node.type))
                    raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)

                # Requirements
                def get_req_type(req):
                    return next((n[req] for n in node.type_definition.requirements if req in n))['relationship']

                for req in node.requirements:
                    name, value = list(req.items())[0]
                    target = value['node'] if isinstance(value, dict) else value

                    req_type = get_req_type(name)
                    logger.debug('Detected requirement in node [{0}] of type [{1}] - target: [{2}], requirement type: [{3}]'.format(
                        node.name, node.type, target, req_type))

                    if req_type == ToscaRequirementTypes.REL_CONNECT:
                        nodeObj.add_connection(target)
                    if req_type == ToscaRequirementTypes.REL_DEPEND:
                        nodeObj.add_depend(target)
                    if req_type == ToscaRequirementTypes.REL_HOST:
                        nodeObj.host = target                        
                    if req_type == ToscaRequirementTypes.REL_ATTACH:
                        location = value['relationship']['properties']['location']
                        nodeObj.add_volume(target, location)

                # each node maintains a copy of the template (?)
                nodeObj.tpl = template

                template.push(nodeObj)

            ToscaParser._add_pointer(template)
            ToscaParser._add_back_links(template)
            ToscaParser._add_extension(template)

            # update container nodes about software nodes they are hosting
            # this feature will be necessary to understand if a container node
            # hosts at least one software node and then it needs to be "toskosed"
            ToscaParser._update_hosted_nodes(template)

            return template

        except ValueError as err:
            logger.exception(err)
            raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)
        
        # an error is occurred during the built-in validation of toscaparser's ToscaTemplate
        except ValidationError as err:
            # search the error line in the report
            error_msg = None
            for item in str(err).split("\n"):
                for validation_error in _VALIDATION_ERRORS.keys():
                    if validation_error in item:
                        error_msg = item.replace(validation_error+':', '')
                        break
            if error_msg is not None:
                logger.error('{}'.format(error_msg))
            else:
                logger.error('An unknown error occurred during the validation of the manifest: {}'.format(err))
            
            raise ParsingError(CommonErrorMessages._DEFAULT_PARSING_ERROR_MSG)
