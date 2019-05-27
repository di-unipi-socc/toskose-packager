import os
import collections
import copy
from enum import Enum, auto
from configparser import ConfigParser

from app.tosca.model.relationships import HostedOn

from app.common.logging import LoggingFacility
from app.common.exception import SupervisordConfigGeneratorError
from app.common.exception import FatalError
from app.common.commons import CommonErrorMessages


logger = LoggingFacility.get_instance().get_logger()

_SUPERVISORD_UNIT_TEMPLATE_PATH = 'templates/supervisord.unit.conf'

_BASE_COMMAND = '/bin/sh -c '
_BASEDIR_STDOUT_LOGFILE = '/toskose/apps'

# TODO better is they can be configured from external
_SUPERVISORD_PROGRAM_TEMPLATE = collections.OrderedDict([
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


class SupervisordTemplateType(Enum):
    Unit = auto()
    Manager = auto()

def _build_unit_config(tosca_model=None, node_name=None, output_dir=None, 
                       config_name=None):
    """ 
    Build the Supervisord configuration file for a toskose-unit container. 
    
    Args:
        tosca_model (str): The model of the TOSCA-based application.
        node_name (str): The name of the TOSCA node for which the conf is generated.
        output_dir (str): The path where the Supervisord config will be writed in.
        config_name (str): The name of the Supervisord config file generated (default: 'supervisord.conf')
    """

    if tosca_model is None:
        raise TypeError('The TOSCA model must be provided.')
    if node_name is None:
        raise TypeError('A container name must be provided.')
    if output_dir is None:
        raise TypeError('An output path must be provided.')
    if output_dir:
        if not os.path.exists(output_dir):
            raise ValueError('The given output path does\'s not exist')

    if config_name is None:
        config_name = 'supervisord.conf'

    if next((x for x in tosca_model.containers if x.name == node_name), None) is None:
        logger.error('Tosca container node [{0}] doesn\'t exist in the model representing [{1}] application'.format(
            node_name, tosca_model.name))
        raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    logger.debug('Building the supervisord.conf for [{0}] node'.format(node_name))

    try:

        config = ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), _SUPERVISORD_UNIT_TEMPLATE_PATH))
        
        for software in tosca_model.software:
            if isinstance(software.host, HostedOn) and software.host.to == node_name:
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

                        # supervisord configuration file base template
                        template = dict(_SUPERVISORD_PROGRAM_TEMPLATE)
                        template_updated = {
                            'command': _BASE_COMMAND + '\'' + command + '\'',
                            'process_name': '{0}-{1}'.format(software.name, interface_name),
                            'stdout_logfile': os.path.join(
                                _BASEDIR_STDOUT_LOGFILE,
                                software.name,
                                'logs',
                                '{0}-{1}.log'.format(software.name, interface_name)
                            ),
                        }

                        template.update(template_updated)
                        config[section_name] = template
        
        config_file_path = os.path.join(output_dir, config_name)

        # Write the Supervisord config
        with open(config_file_path, "w") as config_file:
            config.write(config_file)

    except Exception as err:
        logger.exception(err)
        raise SupervisordConfigGeneratorError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

def build_config(type, **kwargs):
    """ Generate the Supervisord configuration file. 
    
    Args:
        type (Enum): The type of Supervisord configuration to be generated.
            - Unit: Supervisord configuration for the toskose-unit component.
            - Manager: Supervisord configuration for the toskose-manager component.
    """

    if type == SupervisordTemplateType.Unit:
        _build_unit_config(**kwargs)
    else:
        logger.error('Supervisord Configuration type [{}] is invalid'.format(type))
        raise SupervisordConfigGeneratorError(CommonErrorMessages._DEFAULT_SUPERVISORD_CONFIG_GEN_ERROR_MSG)