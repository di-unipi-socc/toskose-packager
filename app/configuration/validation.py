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

    @staticmethod
    def _validate_data(config, tosca_model):
        """ Validate data in the Toskose configuration against the tosca model nodes. """

        invalid = False

        # nodes
        for container in tosca_model.containers:
            if container.name not in config['nodes']:
                logger.warn('Missing [{}] node data from the configuration file'.format(
                    container.name
                ))
                invalid = True

        # manager
        if 'manager' not in config:
            logger.warn('Missing manager data from the configuration file')
            invalid = True

        return invalid

    def _handle_error(self, error):
        if 'is a required property' in error.message:
            extracted = re.findall(r"\'(.*?)\'", error.message)
            raise PartialValidationError('{} field is missing'.format(
                extracted[0] if extracted else 'unknown'
            ))
        else:
            raise ValidationError(error.message)
        

    def validate_config(self, config, tosca_model=None):
        """ Validate a Toskose configuration file """

        try:
            jsonschema.validate(instance=config, schema=self._config_schema)
            if tosca_model is not None:
                if ConfigValidator._validate_data(config, tosca_model):
                    raise PartialValidationError('Missing data from the configuration file')
        except jsonschema.exceptions.ValidationError as err:
            self._handle_error(err)
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
