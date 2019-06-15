""" 
The module where the app's context is built.
"""

import os
import shutil
from itertools import zip_longest

import app.common.constants as constants
from app.common.commons import CommonErrorMessages
from app.common.exception import FatalError, AppContextGenerationError
from app.common.logging import LoggingFacility
from app.supervisord.configurator import build_config
from app.tosca.model.artifacts import File
from app.tosca.model.relationships import HostedOn

logger = LoggingFacility.get_instance().get_logger()

def multi_copy(srcs, dsts, make_srcs=False, make_dsts=True, fixed_head=False):
    """ copying multiple paths between each other 
    
    Args:
        srcs (list): A list of source paths.
        dsts (list): A list of destination paths.
        make_srcs (bool): Create the source paths. [default: True]
        make_dsts (bool): Create the destination paths. [default: True]
        fixed_head (bool): if lists are of different size, it replaces
            with list head the missing items of the shortest list, otherwise
            it replaces by the list tail. [default: False]
    """
    
    idx = 0 if fixed_head else -1
    if len(srcs) > len(dsts):
        fixed = dsts[idx]
    elif len(srcs) < len(dsts):
        fixed = srcs[idx]
    else:
        fixed = None
    
    for src, dst in zip_longest(srcs, dsts, fillvalue=fixed):
        if make_srcs and not os.path.exists(src):
            os.makedirs(src, exist_ok=True)
        if make_dsts and not os.path.exists(dst):
            os.makedirs(dst, exist_ok=True)
        shutil.copy2(src, dst)
        logger.debug('Copied [{0}] in [{1}]'.format(src, dst))

def _build_manager_context(context_path, manifests=None, configs=None, imports=None,
                           manifest_dirs=None, config_dirs=None, imports_dirs=None):
    """ Build the app context for the manager """

    if config_dirs is None:
        config_dirs = [os.path.join(context_path, constants.DEFAULT_MANAGER_CONFIG_DIR)]
    multi_copy(configs, config_dirs)
    
    if manifest_dirs is None:
        manifest_dirs = [os.path.join(context_path, constants.DEFAULT_MANAGER_MANIFEST_DIR)]
    multi_copy(manifests, manifest_dirs)

    if imports_dirs is None:
        imports_dirs = [os.path.join(context_path, constants.DEFAULT_MANAGER_MANIFEST_DIR)]
    multi_copy(imports, imports_dirs) 

def _build_unit_context(context_path, container):
    
    # searching the software nodes hosted on the current container
    # note: toskose-manager node doesn't host any sw node
    for software in container.hosted:
        software_dir = os.path.join(context_path, software.name)

        # generate hosted component root dir
        # /<component_name>
        # /toskose
        # in the initializer script, during the "toskoserization" of the new images

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


def build_app_context(context_path, tosca_model):
    """ 
    Generate the app's context.
    
    This logic generates the directories structure that will be used by a container runtime engine 
    (e.g. Docker) for building the "toskosed" images.
    
    An example of an app's context for a TOSCA-based application:

    /
    --/<component_name> 
    --/...
    --/<component_name>
    --/toskose
    ----/apps
    ------/<component_name>
    --------/<artifacts>          (containing the artifacts associated to the component)
    --------/<scripts>            (containing the scripts for the lifecycle operations)
    --------/<logs>               (containing the logs associated to the component, managed by supervisord)
    ------/...
    ------/<component_name>
    ----/supervisord
    ------/bundle                 (containing the supervisord exec + interpreter)
    ------/config
    --------/supervisord.conf     (the supervisord configuration)
    ------/logs                   (supervisord logs)
    ------/entrypoint.sh          (the entrypoint for starting supervisord)

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

    # build app's context root directory
    root_dir = os.path.join(context_path, tosca_model.name)
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir, ignore_errors=True)
    os.makedirs(root_dir)

    for container in tosca_model.containers:

        # initialize the app's context for the current container
        node_dir = os.path.join(root_dir, container.name)
        os.makedirs(node_dir)

        # toskose-manager container
        if container.is_manager:
            _build_manager_context(
                context_path=node_dir,
                manifests=[tosca_model.manifest_path],
                configs=[tosca_model.toskose_config_path],
                imports=sum([list(entry.values()) for entry in tosca_model.imports], [])
            )
        else:
            _build_unit_context(
                context_path=node_dir,
                container=container
            )

            # generate the Supervisord's configuration file
            build_config(
                container=container,
                context_path=node_dir)
        
            logger.debug('Generated supervisord.conf for container node [{}]'.format(container.name))
