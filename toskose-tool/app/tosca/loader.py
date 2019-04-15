import os
import sys
from toscaparser.prereq.csar import CSAR
from app.common.logging import LoggingFacility
from app.common.exception import ToscaFileNotFoundError
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError
from app.common.commons import suppress_stderr


logger = LoggingFacility.get_instance().get_logger()


class FileType(object):
    """
    CSAR: full TOSCA CSAR archive (including scripts, manifest)
    YAML: partial TOSCA archive (including only the manifest)
    """
    CSAR = ".zip", ".ZIP", ".csar", ".CSAR"
    YAML = ".yml", ".yaml"


class ToscaLoader():
    """ Load and validate a .CSAR archive  """

    def __init__(self, archive_path):

        self._archive_path = archive_path
        
        self._manifest_file = None
        self._csar_dir_path = None
        self._csar_metadata = None
        self._is_csar = False

        self._load()

    def _load(self):
        """ Load the .CSAR archive """

        """ File Validation """
        if not os.path.isfile(self._archive_path):
            raise ToscaFileNotFoundError("Missing CSAR/yml file")

        """ Recognizing extension """
        if self._archive_path.lower().endswith(FileType.CSAR):
            self._load_csar()
        elif self._archive_path.lower().endswith(FileType.YAML):
            self._load_yaml()
        else:
            file_name, extension = os.path.splitext(self._archive_path)
            err_msg = '{0} is an invalid file extension'.format(extension) if extension \
                 else 'file extension is not recognized'
            logger.error(err_msg)
            raise ToscaParsingError(err_msg)

    def _load_csar(self):
        """ Load a .CSAR archive """

        # suppress tosca-parser messages noise
        with suppress_stderr():
        
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
            self._manifest_file = csar.get_main_template()
            self._csar_dir_path = csar.temp_dir
            self._csar_metadata = csar.get_metadata()
            self._is_csar = True

    def _load_yaml(self):
        """ Load a single yaml manifest (without the csar) """

        self._csar_dir_path, self._manifest_file = os.path.split(self._archive_path)

        #TODO tosca-parser accepts only .csar (?) validation is impossible

    @property
    def archive_path(self):
        """ The path of the .CSAR archive """
        return self._archive_path

    @property
    def csar_dir_path(self):
        """ The path of the temporary unpacked csar dir """
        return self._csar_dir_path

    @property
    def manifest_file(self):
        """ The name of the yaml manifest """
        return self._manifest_file

    @property
    def manifest_path(self):
        """ the path of the yaml manifest"""
        return os.path.join(self._csar_dir_path, self._manifest_file)

    @property
    def csar_metadata(self):
        """ Metadata about the validated .CSAR archive """
        return self._csar_metadata

    @property
    def is_csar(self):
        """ Return true if the loaded file is a .CSAR archive """
        return self._is_csar

    def get_paths(self):
            """ Return all the paths in a dict """
            return {
                'archive': self._archive_path,
                'csar_dir': self._csar_dir_path,
                'manifest': self._manifest_file,
            }