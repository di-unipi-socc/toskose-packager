import os
import ruamel.yaml

from app.common.logging import LoggingFacility
from app.common.exception import ParsingError


logger = LoggingFacility.get_instance().get_logger()


class Configurator:
    """
    The DataLoader class is used to load and parse the Toskose YAML configuration
    from a given file name.
    """

    def __init__(self):
        pass

    def load(self, path):
        """ Load the configuration from a given file.
        
        Args:
            path (str): The path to the configuration file.

        Returns:
            config: A dict containing the data loaded from the configuration file.
        """

        if not os.path.exists(path):
            raise ValueError('The given path {} doesn\'t exists.'.format(path))

        logger.debug('Loading data from {}'.format(path))
        try:
            with open(path, 'r') as f:
                return ruamel.yaml.load(f, Loader=ruamel.yaml.Loader)
        except ruamel.yaml.error.YAMLError as err:
            raise ParsingError('Failed to parse {}'.format(path))

    def dump(self, data, path):
        """ """

        if not data:
            raise ValueError('The given data is empty.')

        logger.debug('Dumping data to {}'.format(path))
        try:
            with open(path, 'w') as f:
                ruamel.yaml.dump(data, f, Dumper=ruamel.yaml.Dumper)
        except ruamel.yaml.error.YAMLError as err:
            raise ParsingError('Failed to dump in {}'.format(path))

        return path
        
