import json
import os
import jsonschema
import re
from functools import reduce

import app.common.constants as constants
from app.common.logging import LoggingFacility
from app.common.exception import ValidationError
from app.common.exception import PartialValidationError
from app.common.exception import FatalError
from app.common.commons import CommonErrorMessages


logger = LoggingFacility.get_instance().get_logger()


class ConfigValidator:
    def __init__(self, schema_path=None):
        if schema_path is None:
            schema_path = os.path.join(
                os.path.dirname(__file__),
                constants.DEFAULT_TOSKOSE_CONFIG_SCHEMA_PATH,
            )
        if not os.path.exists(schema_path):
            raise FileNotFoundError('Toskose configuration schema not found.')
        with open(schema_path, 'r') as f:
            try:
                self._config_schema = json.load(f)
            except json.decoder.JSONDecodeError as err:
                logger.error(err)
                raise FatalError('The toskose configuration schema is corrupted. Validation cannot be done.')
            except Exception as err:
                logger.exception(err)
                raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)   


    def _validate_nodes(config, tosca_model):
        for container in tosca_model.containers:
            
            if container.name not in config['nodes']:
                raise ValidationError('Missing node [{}] in the configuration.'.format(
                    container.name))
            
            if 'docker' not in config['nodes'][container.name]:
                raise ValidationError('Missing docker section in the node [{}]'.format(
                    container.name))


    def validate_config(self, config, tosca_model=None):
        """ Validate a Toskose configuration file """

        try:
            jsonschema.validate(instance=config, schema=self._config_schema)
            # if tosca_model is not None:
            #     ConfigValidator._validate_nodes(config, tosca_model)
        except jsonschema.exceptions.ValidationError as err:
            raise ValidationError(err.message)
        except jsonschema.exceptions.SchemaError as err:
            logger.error(err)
            raise FatalError('The toskose configuration schema is corrupted. Validation cannot be done.')

    def get_schema_metadata(self):
        filtered = ['nodes', 'manager']
        return list(filter(lambda x: x not in filtered, self._config_schema['properties'].keys()))

    def get_schema_node_api_data(self):
        return list(self._config_schema['definitions']['node']['properties']['api']['properties'].keys())

    def get_schema_node_docker_data(self):
        return list(self._config_schema['definitions']['node']['properties']['docker']['properties'].keys())
