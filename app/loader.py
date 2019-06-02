import os
import ruamel.yaml
import collections

from app.common.logging import LoggingFacility
from app.common.exception import ParsingError


logger = LoggingFacility.get_instance().get_logger()


class Loader:
    """
    The Loader class is used to load and parse YAML configurations
    from a given file name.
    """

    def __init__(self):
        self._setup_ordered_dict()

    def _setup_ordered_dict(self):
        """ Setup a representer for OrderedDict. 
        https://bitbucket.org/ruamel/yaml/issues/22/how-to-dump-collectionordereddict
        """

        ruamel.yaml.representer.RoundTripRepresenter.add_representer(
            collections.OrderedDict,
            ruamel.yaml.representer.RoundTripRepresenter.represent_ordereddict
        )

    def load(self, path, **kwargs):
        """ Load the configuration from a given file.
        
        Args:
            path (str): The path to the configuration file.

        Returns:
            config: A dict containing the data loaded from the configuration file.
        """

        if not os.path.exists(path):
            raise ValueError('The given path {} doesn\'t exists.'.format(path))

        loading_function = ruamel.yaml.load
        loading_args = { 'Loader': ruamel.yaml.Loader }

        ordered = kwargs.get('ordered', False)
        if ordered:
            loading_args['Loader'] = ruamel.yaml.RoundTripLoader

        trip_load = kwargs.get('print', False)
        if trip_load == True:
            loading_function = ruamel.yaml.round_trip_load
            loading_args = {}

        logger.debug('Loading data from {}'.format(path))
        try:
            with open(path, 'r') as f:
                res = loading_function(f, **loading_args)

                if trip_load:
                    out = ""
                    lines = ruamel.yaml.round_trip_dump(
                        res, 
                        indent=3, 
                        block_seq_indent=3,
                        default_flow_style=None,
                    ).splitlines(True)
                    
                    for line in lines:
                        out += line[3:]
                    return out
                return res

        except ruamel.yaml.error.YAMLError as err:
            raise ParsingError('Failed to parse {}'.format(path))

    def dump(self, data, path, ordered=False):
        """ Dump a yml file to the disk. """

        if not data:
            raise ValueError('The given data is empty.')

        dumper = ruamel.yaml.Dumper
        if ordered:
            dumper = ruamel.yaml.RoundTripDumper
            data = ruamel.yaml.comments.CommentedMap(data)

        logger.debug('Dumping data to {}'.format(path))
        try:
            with open(path, 'w') as f:
                ruamel.yaml.dump(data, f, Dumper=dumper, default_flow_style=False)
        except ruamel.yaml.error.YAMLError as err:
            raise ParsingError('Failed to dump in {}'.format(path))

        return path
        
