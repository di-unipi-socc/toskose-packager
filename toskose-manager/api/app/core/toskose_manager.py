import os
import sys
import logging
import toml
from toml import TomlDecodeError
from schema import Schema, And, Use, Optional, SchemaError

from config import AppConfig
from client.client import ToskoseClientFactory


class MissingConfigurationDataError(Exception):
    """ Raised when there are some missing data in the app configuration """

    def __init__(self, message):
        super().__init__(message)


class ToskoseManager():
    """ A singleton containing the application settings """
    __instance = None

    @staticmethod
    def get_instance():
        """ The static access method """

        if ToskoseManager.__instance == None:
            ToskoseManager()
        return ToskoseManager.__instance

    def __init__(self):
        if ToskoseManager.__instance != None:
            raise Exception('This is a singleton')
        else:
            ToskoseManager.__instance = self

    def load(self, config_path=None):
        self._config_path = self.load_config(config_path)
        self._config = self.parse_config(self._config_path)
        self._config = self.__validate_config(self._config)
        self._nodes = self._config.get('nodes')

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

                config = toml.load(f, _dict=dict)

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

        """ Validate node fields """
        # for node in nodes:
        #     try:
        # TODO USING SCHEMA LIB


        return config

    @property
    def nodes(self):
        return self._nodes

    def get_node_data(self, *, node_id=None, hostname=None, port=None):
        """ returns the configuration file data associated to the node

        data can be obtained by node_id or by hostname and port of the node.

        Args:
            node_id (str): the node identifier.
            hostname (str): the node\'s hostname.
            port (str): the node\'s port.

        Returns:
            result: a tuple (node_id, node_data) containing the node identifier
            and the node\'s data associated.

        """

        if not node_id:
            if not host or not port:
                raise ValueError('hostname and port must be given')
            else:
                for node_id, node_data in self._nodes.items():
                    if node_data.get('hostname') == hostname and \
                        node_data.get('port') == port:
                        return node_id, node_data
                raise MissingConfigurationDataError('no data for the node {0}' \
                    .format(node_id))

        node_data = self._nodes.get(node_id)
        if not node_data:
            raise MissingConfigurationDataError('node {0} not found' \
                .format(node_id))
        return node_id, node_data

    def get_node_client_instance(self, node_id):
        """ returns the client instance for a node """

        node = self._nodes.get(node_id)
        if not node:
            raise MissingConfigurationDataError('node {0} not found' \
                .format(node_id))

        """ assuming node fields are previously validated """
        return ToskoseClientFactory.create(
            type=AppConfig._CLIENT_PROTOCOL,
            host=node['hostname'],
            port=node['port'],
            username=node['username'],
            password=node['password']
        )
