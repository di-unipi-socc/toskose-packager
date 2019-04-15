import os
from toscaparser.tosca_template import ToscaTemplate
from app.common.logging import LoggingFacility
from app.common.exception import ToscaFileNotFoundError
from app.common.exception import ToscaValidationError
from app.common.commons import Alerts


logger = LoggingFacility.get_instance().get_logger()

_required_attrs = [
    "topology_template",
    "nodetemplates",
]

class ToscaValidator():

    def __init__(self, manifest_path):
        self._manifest_path = manifest_path

        if not os.path.isfile(manifest_path):
            raise ToscaFileNotFoundError('Missing TOSCA YAML manifest')
        
        try:
            self._tt = ToscaTemplate(manifest_path)
        except ValueError as err:
            logger.exception(err)
            raise

    def validate(self):

        validated = True

        # print(self._tt.tpl)

        # TODO vedi tosca_parser (toskerer)



        # print(list(filter(lambda x: not x.startswith('__') or not x.startswith('_'), dir(self._tt))))

        # for attr in _required_attrs:
        #     if not hasattr(self._tt, attr):
        #         validated = False  
        #         err_msg = 'Malformed manifest: missing {0}'.format(attr)
        #         logger.error(err_msg)
        #         errors.append({'error': err_msg, 'alert': Alerts.Failure})

        # TODO other validations
        # tosca-parser doesn't validate missing scripts/folders
        # what else?

        # # log errors

        return validated

    @property
    def manifest_path(self):
        return self._manifest_path
        