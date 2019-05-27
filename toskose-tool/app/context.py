""" 
The module where the app's context is built.
"""

import os
import shutil

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.common.exception import FatalError
from app.common.commons import CommonErrorMessages
from app.tosca.model.relationships import HostedOn
from app.tosca.model.artifacts import File
from app.supervisord.configurator import SupervisordTemplateType, build_config


logger = LoggingFacility.get_instance().get_logger()


def build_app_context(context_path, tosca_model):
    """ 
    Generate the app's context.
    
    This logic generates the directories structure that will be used by a container runtime engine 
    (e.g. Docker) for building the "toskosed" images.
    
    An example of an app's context for a TOSCA-based application:

    /
    --/toskose
    ----/<application_name>
    ------/<container_name>         (related to the tosca container node)
    --------/<component_name>       (related to the tosca software node hosted on)
    ----------/<artifacts>          (containing the artifacts associated to the component)
    ----------/<scripts>            (containing the scripts for the lifecycle operations)
    ----------/<logs>               (containing the logs associated to the component, managed by supervisord)
    --------/ ...
    --------/<component_name>        
    --------/supervisord.conf       (the supervisord configuration)

    Note: the structure above will be "merged" during the docker build process with a base structure already 
            present in the toskose-unit image (see toskose-unit module). The latter contains a base logic for
            Supervisord and it's used as a base image for generating the final "toskosed" image
            (i.e. the image associated to the tosca container node "enriched" with the toskose/Supervisord logic
            by meaning of docker multi-stage feature, necessary to handling multi-components hosted on the same container).

    Args:
        - context_path (str): The path in which the docker's app context will be placed.
        - tosca_model (object): The model representing the Tosca application.
    """

    if not os.path.exists(context_path):
        raise ValueError('The output path [{}] is invalid or doesn\'s exist.'.format(context_path))
    if tosca_model is None:
        raise TypeError('The TOSCA model must be provided.')

    logger.debug('Building [{0}] app context in [{1}]'.format(tosca_model.name, context_path))

    try:

        # build app's context root directory
        root_dir = os.path.join(context_path, tosca_model.name)
        if os.path.exists(root_dir):
            shutil.rmtree(root_dir, ignore_errors=True)
        os.makedirs(root_dir)

        for container in tosca_model.containers:

            # initialize the app's context for the current container
            node_dir = os.path.join(root_dir, container.name)
            os.makedirs(node_dir)

            # toskose-manager
            if container.is_manager:
                
                # copy the toskose configuration (in toskose-manager context)
                shutil.copy2(tosca_model.toskose_config_path, node_dir)
                logger.debug('Copied the toskose config [{0}] in [{1}]'.format(
                    os.path.basename(tosca_model.toskose_config_path), node_dir))

                # copy the tosca manifest (in toskose-manager context)
                shutil.copy2(tosca_model.manifest_path, node_dir)
                logger.debug('Copied the tosca manifest [{0}] in [{1}]'.format(
                    os.path.basename(tosca_model.manifest_path), node_dir))

            else:
                for software in tosca_model.software:
                    # searching the software nodes hosted on the current containe
                    if isinstance(software.host, HostedOn) and software.host.to == container.name:
                        software_dir = os.path.join(node_dir, software.name)
                        
                        # copy artifacts
                        artifacts_dir = os.path.join(software_dir, 'artifacts')
                        os.makedirs(artifacts_dir)
                        for artifact in software.artifacts:
                            shutil.copy2(
                                artifact.file_path, 
                                os.path.join(artifacts_dir, os.path.basename(artifact.file_path)))

                        # copy scripts (lifecycle operations) 
                        interfaces_dir = os.path.join(software_dir, 'scripts')
                        os.makedirs(interfaces_dir)

                        # e.g.
                        # interfaces:
                        #   Standard:                                   # interfaces group
                        #     create:                                   # interface
                        #       implementation: /path/to/impl           # cmd (File Object)
                        #       inputs:                                 # inputs -> container envs
                        #         repo: <url_repo>
                        #         branch: { get_input: api_branch }     # function

                        for _, inter_group_content in software.interfaces.items():
                            # multiple interfaces groups can co-exists, not only the "standard"
                            for interface_name, interface_content in inter_group_content.items():

                                shutil.copy2(
                                    interface_content['cmd'].file_path, 
                                    os.path.join(
                                        interfaces_dir, 
                                        os.path.basename(interface_content['cmd'].file_path)))

                                # add interface's inputs name:path as an env variable
                                if 'inputs' in interface_content:
                                    for k,v in interface_content['inputs'].items():
                                        if isinstance(v, File):
                                            logger.debug('Detected the interface [{0}] associated to the artifact [{1}]'.format(
                                                interface_name, v.name))
                                            
                                            # change the path of the file according to the running container structure
                                            v = os.path.join(
                                                '/toskose/apps/{}/artifacts'.format(software.name),
                                                os.path.basename(v.file_path))
                                        
                                        container.add_env('INPUT_{}'.format(k.upper()), v)

                        # initialize logs
                        logger.debug('Initializing logs for component [{0}] hosted on container [{1}]'.format(
                            software.name, container.name))
                        logs_path = os.path.join(software_dir, 'logs')
                        log_name ='{0}.log'.format(software.name)
                        os.makedirs(logs_path)
                        open(os.path.join(logs_path, log_name), 'w').close  

                # generate the Supervisord's configuration file
                build_config(
                    SupervisordTemplateType.Unit,
                    tosca_model=tosca_model,
                    node_name=container.name,
                    output_dir=node_dir)
                
                logger.debug('Generated supervisord.conf for container node [{}]'.format(container.name))

                # Validate the component(s) context
                _validate_context(node_dir)

    except (TypeError, OSError) as err:
        logger.exception(err)
        raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)


def _validate_context(context_path, supervisord_config='supervisord.conf'):
    """ Validate the application context for a container node. 
    
    e.g. if the supervisord configuration exists, if there is at least one tosca software component

    Args:
        context_path (str): The path for the app's context.
        supervisord_config (str): The name of the Supervisord configuration file. (default: 'supervisord.conf')
    """

    # there is at least one TOSCA node
    if not os.listdir(context_path):
        logger.error('Invalid context: no components found in [{}]'.format(context_path))
        raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    dir_files = [f for f in os.listdir(context_path) \
        if os.path.isfile(os.path.join(context_path, f))]

    # supervisord configuration file
    if supervisord_config not in dir_files:
        logger.error('Invalid context: {} not found'.format(supervisord_config))
        raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
