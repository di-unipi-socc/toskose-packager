import os
import sys
import logging
import toml
from toml import TomlDecodeError


logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

config_name = 'toskose.toml'
app_dir = 'toskose'
basedir = os.path.abspath(os.path.dirname(__file__))

_default_config_paths = (
    os.path.join('etc', config_name),
    os.path.join('etc', app_dir, config_name),
    os.path.join(app_dir, config_name)
)


class ToskoseManager():
    """ A singleton containing the application settings """
    __instance = None

    @staticmethod
    def getInstance():
        """ The static access method """

        if ToskoseManager.__instance == None:
            ToskoseManager()
        return ToskoseManager.__instance

    def __init__(self, config_path_manual=None):
        if ToskoseManager.__instance != None:
            raise Exception('This is a singleton')

        self._config_path = config_path_manual
        self.__load_config()
        self.__parse_config()

    def __load_config(self):
        """ Load the configuration file """

        _env_config_path = os.environ.get('TOSKOSE_MANAGER_CONFIG_PATH')
        _env_mode = os.environ.get('TOSKOSE_MANAGER_MODE')

        if not self._config_path or not os.path.exists(self._config_path):
            self._config_path = _env_config_path
            if not self._config_path:
                """ search in default paths """
                for path in _default_config_paths:
                    if os.path.exists(path):
                        self._config_path = path
                        break

        if not self._config_path and _env_mode == 'dev':
            logging.warning('-- development mode -- loaded a test config')
            self._config_path = \
                os.path.join(os.path.abspath('./resources/config'), config_name)
        else:
            sys.exit('missing configuration file {0}'.format(config_name))


    def __parse_config(self):
        """ Parse the configuration file """

        with open(self._config_path, 'r') as f:
            try:

                logging.info('Parsing configuration file {0}' \
                    .format(self._config_path))

                self._config = self.__validate_config(toml.load(f, _dict=dict))

                # TODO build data structures


            except TypeError as err:
                sys.exit('failed to open the configuration file {0}' \
                    .format(self._config_path))
            except TomlDecodeError as err:
                sys.exit('failed to parse the configuration file {0}\nError: {1}' \
                    .format(self._config_path, err))

    def __validate_config(self, config):
        """ Validate the configuration """

        """ Load Nodes """
        nodes = config.get('nodes')
        if not nodes:
            sys.exit('ERROR! missing nodes field (required)')

        # TODO validation

        return config

    @property
    def nodes(self):
        return self._nodes

    def reload(self):
        logging.info('Reloading configuration..')
        self.__load_config()
        self.__parse_config()
