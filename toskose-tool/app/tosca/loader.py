import os
import sys
from toscaparser.prereq.csar import CSAR
from app.common.logging import LoggingFacility
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError


logger = LoggingFacility.get_instance().get_logger()


class FileType(object):
    """
    CSAR: full TOSCA CSAR archive (including scripts, manifest)
    YAML: partial TOSCA archive (including only the manifest)
    """
    CSAR = ".zip", ".ZIP", ".csar", ".CSAR"


class ToscaParser():
    """ Load and validate a .CSAR archive  """

    def __init__(self, archive_path):

        self._archive_path = archive_path
        
        self._manifest_path = None
        self._csar_metadata = {}

        self._load()
        self._validation()

    def _load(self):
        """ Load the .CSAR archive """

        """ File Validation """
        if not os.path.isfile(self._archive_path):
            raise ToscaParsingError("Missing CSAR/yml file")

        """ Recognizing extension """
        if self._archive_path.lower().endswith(FileType.CSAR):
            self._load_csar()
        else:
            err_msg = 'Invalid file extension'
            logger.error(err_msg)
            raise ToscaParsingError(err_msg)

    def _load_csar(self):
        """ """
        
        csar = CSAR(self._archive_path)

        try:

            """ TOSCA-parser validation """
            logger.info('Validating {0}...'.format(self._archive_path))
            csar.validate()

        except ValueError as err:
            logger.debug(err)

            # tosca-parser bug validation workaround
            if not str(err).startswith("The resource") or \
               not str(err).endswith("does not exist."):
                raise ToscaValidationError('Failed to validate .CSAR archive: {0}'.format(err))

        logger.info('{0} is valid. Decompression started...'.format(self._archive_path))

        csar.decompress()
        self._manifest_path = os.path.join(csar.temp_dir, csar.get_main_template())
        self.csar_metadata = {
            **{
                'temp_dir': csar.temp_dir,
            },
            **csar.get_metadata()
        }

    def _validation(self):
        """ Toskose custom validation """
        pass

    @property
    def archive_path(self):
        """ The path of the .CSAR archive """
        return self._archive_path

    @property
    def manifest_pat(self):
        """ The path of the yaml manifest for the validated .CSAR archive """
        return self._manifest_path

    @property
    def csar_metadata(self):
        """ Metadata about the validated .CSAR archive """
        return self._csar_metadata

    @property
    def 
