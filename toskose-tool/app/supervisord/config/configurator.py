import os
import collections
import copy
from enum import Enum, auto
from configparser import ConfigParser

from app.common.logging import LoggingFacility
from app.common.exception import SupervisordConfigGeneratorError
from app.common.commons import CommonErrorMessages


logger = LoggingFacility.get_instance().get_logger()

_SUPERVISORD_UNIT_TEMPLATE_PATH = 'templates/supervisord.unit.conf'

_BASE_COMMAND = '/bin/sh -c '
_BASEDIR_STDOUT_LOGFILE = '/toskose/apps'

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
    """ Supervisord config templates types
    
    - Unit: Supervisord config for "toskosed" images
    """
    Unit = auto()

class SupervisordConfigGenerator:

    def __init__(self, 
        config_path, 
        config_name='supervisord.conf'):

        self._config_path = config_path
        self._config_name = config_name

        self._config = ConfigParser()

    def build(self, type, **kwargs):
        """ Build the Supervisord config """

        try:

            if type == SupervisordTemplateType.Unit:
                self._config.read(os.path.join(os.path.dirname(__file__), _SUPERVISORD_UNIT_TEMPLATE_PATH))
                self._build_unit(**kwargs)
            else:
                raise SupervisordConfigGeneratorError('Supervisord Configuration type not recognized')

        except Exception as err:
            logger.exception(err)
            raise SupervisordConfigGeneratorError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    def _build_unit(self, **kwargs):

        components_data = kwargs['components_data']

        try:

            for component_data in components_data:
                name = component_data['name']
                lifecycle_operations = component_data['interfaces']
                for operation, command in lifecycle_operations.items():
                    section_name = 'program:{0}-{1}'.format(name, operation)
                    template = dict(_SUPERVISORD_PROGRAM_TEMPLATE)
                    template_updated = {
                        'command': _BASE_COMMAND + '\'' + command + '\'',
                        'process_name': '{0}-{1}'.format(name, operation),
                        'stdout_logfile': os.path.join(
                            _BASEDIR_STDOUT_LOGFILE,
                            name,
                            'logs',
                            '{0}-{1}.log'.format(name, operation)
                        ),
                    }

                    template.update(template_updated)

                    self._config[section_name] = template

            if not os.path.exists(self._config_path):
                logger.error('{0} not exists'.format(self._config_path))
                raise SupervisordConfigGeneratorError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
            
            config_file_path = os.path.join(self._config_path, self._config_name)

            # Write the Supervisord config
            with open(config_file_path, "w") as config_file:
                self._config.write(config_file)

        except Exception as err:
            logger.exception(err)
            raise SupervisordConfigGeneratorError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)