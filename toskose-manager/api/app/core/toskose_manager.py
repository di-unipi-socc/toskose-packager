import os
import sys
import logging
import toml
from toml import TomlDecodeError

from config import AppConfig


class ToskoseManager():
    """ A singleton containing the application settings """
    __instance = None

    @staticmethod
    def getInstance():
        """ The static access method """

        if ToskoseManager.__instance == None:
            ToskoseManager()
        return ToskoseManager.__instance

    def __init__(self, config_path=None):
        if ToskoseManager.__instance != None:
            raise Exception('This is a singleton')

        """ load app configuration """
        self._config_path = self.load_config(config_path)
        self._config = self.parse_config(self._config_path)

    def load_config(self, config_path=None):
        """ Load the configuration file """

        if not config_path or not os.path.exists(config_path):
            """ no manual path fetched or it is not valid """

            config_path = AppConfig._APP_CONFIG_PATH
            if not config_path or not os.path.exists(config_path) \
                and AppConfig._APP_MODE == 'development':
                """ env variable not valid, just load a test config """

                config_path = \
                    os.path.join(
                        os.path.abspath('./resources/config'),
                        AppConfig._APP_CONFIG_NAME)
            else:
                sys.exit('missing configuration file {0}'.format(config_name))

        return config_path

    def parse_config(self, config_path):
        """ Parse the configuration """

        config = None
        try:
            with open(config_path, 'r') as f:

                logging.info('Parsing configuration file {0}' \
                    .format(self._config_path))

                config = self.__validate_config(toml.load(f, _dict=dict))

        except TypeError as err:
            sys.exit('failed to open the configuration file {0}' \
                .format(self._config_path))
        except TomlDecodeError as err:
            sys.exit('failed to parse the configuration file {0}\nError: {1}' \
                .format(self._config_path, err))
        return config

    def __validate_config(self, config):
        """ Validate the configuration """

        """ Validate Nodes """
        nodes = config.get('nodes')
        if not nodes:
            sys.exit('ERROR! missing nodes field (required)')

        return config

    @property
    def nodes(self):
        return self._nodes

    def reload(self):
        logging.info('Reloading configuration..')
        self._config_path = self.load_config()
        self._config = self.parse_config(self._config_path)
