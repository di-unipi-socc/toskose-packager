import collections
import copy
import os
from configparser import ConfigParser
from enum import Enum, auto

from app.common.commons import CommonErrorMessages
from app.common.exception import FatalError, SupervisordConfigGeneratorError
from app.common.logging import LoggingFacility
from app.tosca.model.relationships import HostedOn

logger = LoggingFacility.get_instance().get_logger()


DEFAULT_CONFIG_NAME = 'supervisord.conf'
DEFAULT_SUPERVISORD_UNIT_TEMPLATE = 'templates/supervisord.unit.conf'
DEFAULT_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__))

DEFAULT_BASE_COMMAND = '/bin/sh -c '
DEFAULT_BASEDIR_STDOUT_LOGFILE = '/toskose/apps'

# TODO better is they can be configured from external
DEFAULT_SUPERVISORD_PROGRAM_TEMPLATE = collections.OrderedDict([
    ('command', None),
    ('process_name', None),
    ('numprocs', '1'),
    ('umask', '022'),
    ('priority', '999'),
    ('autostart', 'false'),
    ('startsecs', '0'),
    ('startretries', '3'),
    ('autorestart', 'false'),
    ('exitcodes', '0'),
    ('stopsignal', 'TERM'),
    ('stopwaitsecs', '10'),
    ('stopasgroup', 'false'),
    ('killasgroup', 'false'),
    ('user', 'root'),
    ('redirect_stderr', 'true'),
    ('stdout_logfile', None),
    ('stdout_logfile_maxbytes', '1MB'),
    ('stdout_logfile_backups', '10'),
    ('stdout_capture_maxbytes', '1MB'),
    ('stdout_events_enabled', 'false'),
    ('serverurl', 'AUTO')
])


def _build_standalone_config(config, container):
    """ 
    Container has no hosted components, it's a standalone container.
    The CMD command of the container is mapped as the only Supervisord's program.
    We're assuming that the CMD command is a fully runnable command that includes 
    also the shell executable.
    """

    if not container.cmd:
        raise ValueError('The container node must have a runnable command')

    template = dict(DEFAULT_SUPERVISORD_PROGRAM_TEMPLATE)
    template.update({
        'command': container.cmd,
        'process_name': '{0}-{1}'.format(container.name, 'default'),
        'stdout_logfile': os.path.join(
            '/toskose',
            '{}.log'.format(container.name)
        ),
    })
    section_name = 'program:{0}-{1}'.format(container.name, 'default')
    config[section_name] = template

    return config

def _build_hosted_config(config, container):
    """ Build a configuration for a container with software components hosted on. """

    for software in container.hosted:
        for inter_group_name, inter_group_content in software.interfaces.items():
            # multiple interfaces groups can co-exists, not only the "standard"
            for interface_name, interface_content in inter_group_content.items():
                # TODO may insert also the inter_group_name in section_name? 
                # conflicts with toskose-manager api?
                section_name = 'program:{0}-{1}'.format(software.name, interface_name)
                
                # change the path of the lifecycle operation according to the container context
                command = os.path.join(
                    '/toskose/apps/{software_node}/scripts'.format(software_node=software.name), 
                    os.path.basename(interface_content['cmd'].file_path)
                )

                template = dict(DEFAULT_SUPERVISORD_PROGRAM_TEMPLATE)
                template_updated = {
                    'command': DEFAULT_BASE_COMMAND + '\'' + command + '\'',
                    'process_name': '{0}-{1}'.format(software.name, interface_name),
                    'stdout_logfile': os.path.join(
                        DEFAULT_BASEDIR_STDOUT_LOGFILE,
                        software.name,
                        'logs',
                        '{0}-{1}.log'.format(software.name, interface_name)
                    ),
                }

                template.update(template_updated)
                config[section_name] = template

    return config

def build_config(container, context_path, config_name=None, template=None):
    """ 
    Build the Supervisord configuration file for managing the container.

    Args:
        container (object): The container node for which the conf is generated.
        context_path (str): The path where the Supervisord config will be writed in.
        config_name (str): The name of the Supervisord config file generated.
            If omitted a default one is generated (e.g. 'supervisord.conf')
        template (str): The path to the Supervisord base template.
            If omitted the default path is taken.
    """

    if context_path:
        if not os.path.exists(context_path):
            raise ValueError('The given {} path does\'s not exist'.format(context_path))
    if config_name is None:
        config_name = DEFAULT_CONFIG_NAME
    if template is None:
        template = os.path.join(DEFAULT_TEMPLATE_DIR, DEFAULT_SUPERVISORD_UNIT_TEMPLATE)

    logger.debug('Building the supervisord.conf for [{0}] node'.format(container.name))
    config = ConfigParser()
    config.read(template)

    # standalone container
    if not container.hosted:
        config = _build_standalone_config(config, container)
    else:
        config = _build_hosted_config(config, container)

    config_path = os.path.join(context_path, config_name)
    with open(config_path, "w") as cfile:
        config.write(cfile)

    logger.debug('Supervisord configuration [{}] built'.format(config_path))