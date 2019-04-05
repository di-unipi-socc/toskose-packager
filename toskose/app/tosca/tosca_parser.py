import os
import sys
from aenum import MultiValueEnum
from toscaparser.prereq.csar import CSAR
from app.config import AppConfig
from app.common.logging import LoggingFacility
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError


logger = LoggingFacility.get_instance().get_logger()


class FileType(MultiValueEnum):
    """
    CSAR: full TOSCA CSAR archive (including scripts, manifest)
    YAML: partial TOSCA archive (including only the manifest)
    """
    CSAR = ".zip", ".ZIP", ".csar", ".CSAR"
    YAML = ".yml", ".YML"


class ToscaParser():
    """  """

    def __init__(self, file_path):

        self.file_path = file_path
        self.current_csar = None
        self.is_only_yaml = False
        
        self._load()

    def _load(self):
        """ Load the .yml manifest (partial) or the .CSAR archive (full) """

        if not os.path.isfile(file_path):
            raise ToscaParsingError("Error: Missing .CSAR/.yml file")

        if file_path.lower().endswith(FileType.CSAR):
            self._load_csar()
        elif file_path.lower().endswith(FileType.YAML):
            self.is_only_yaml = True
            self._load_yml()
        else:
            raise ToscaParsingError('Error: Invalid file extension')


    def _load_csar(self):
        """ """
        
        self.csar = CSAR(self.file_path)

        try:

            logger.info('Validating {0}...'.format(self.file_path))
            self.csar.validate()

        except ValueError as err:
            logger.error('Error: Failed to validate .CSAR archive \n {0}'.format(err))
            raise err
        
        logger.info('{0} is valid. Decompression started...'.format(self.file_path))

        csar.decompress()
    
    def _load_yml(self, file_path):
        print('yaml')
        pass
