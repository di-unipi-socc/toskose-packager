import os
import tempfile
import zipfile
import yaml

from toscaparser.tosca_template import ToscaTemplate
from app.common.logging import LoggingFacility
from app.common.commons import unpack_archive
from app.common.commons import CommonErrorMessages
from app.common.exception import ToscaFileNotFoundError
from app.common.exception import ToscaValidationError
from app.common.exception import ToscaMalformedCsarError
from app.common.exception import ToscaFatalError


logger = LoggingFacility.get_instance().get_logger()

_CSAR_ADMITTED_EXTENSIONS = (".zip", ".csar")

_TOSCA_METADATA_PATH = 'TOSCA-Metadata/TOSCA.meta'
_TOSCA_METADATA_OPTIONAL_KEYS = ('Created-By', 'CSAR-version', 'Description')
_TOSCA_METADATA_REQUIRED_KEYS = ('Entry-Definitions')
_TOSCA_METADATA_MANIFEST_KEY = 'Entry-Definitions'

_required_attrs = [
    "topology_template",
    "nodetemplates",
]

def validate_manifest(manifest_path):

    #tt = ToscaTemplate(self._archive_path)

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

    # # log errorsh

    pass

def validate_csar(csar_path):
    """ """

    # file existence
    if not os.path.isfile(csar_path):
        err_msg = 'Missing .CSAR archive file'
        logger.error(err_msg)
        raise ToscaFileNotFoundError(err_msg)

    # file extension
    if not csar_path.lower().endswith(_CSAR_ADMITTED_EXTENSIONS):
        fname, ext = os.path.splitext(csar_path)
        err_msg = '{0} is an invalid file extension'.format(ext) \
            if ext \
            else 'file extension is not recognized'
        logger.error(err_msg)
        raise ToscaFileNotFoundError(err_msg)

    # validate archive file
    if not zipfile.is_zipfile(csar_path):
        err_msg = '{0} is an invalid or corrupted archive'.format(csar_path)
        logger.error(err_msg)
        raise ToscaFileNotFoundError(err_msg)


    csar_metadata = {}

    # validate csar structure
    with zipfile.ZipFile(csar_path, 'r') as archive:
        filelist = archive.filelist()

        if _TOSCA_METADATA_PATH not in filelist:
            logger.error('{0} does not contain a valid TOSCA.meta'.format(csar_path))
            raise ToscaMalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

        # validate TOSCA.meta
        try:

            csar_metadata = yaml.load(archive.read(_TOSCA_METADATA_PATH))
            if type(csar_metadata) is not dict:
                logger.error('{0} is not a valid dictionary'.format(
                    _TOSCA_METADATA_PATH))
                raise ToscaMalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

        except yaml.YAMLError as err:
            logger.exception(err)
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

        # validate tosca metadata
        for key in ToscaMetadataSchema._TOSCA_METADATA_REQUIRED_KEYS:
            if key not in csar_metadata:
                logger.error('Missing {0} in {1}'.format(key, _TOSCA_METADATA_PATH))
                raise ToscaMalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

        # validate tosca manifest file
        manifest = csar_metadata.get(_TOSCA_METADATA_MANIFEST_KEY, None)
        if manifest is None or manifest not in filelist:
            logger.error('{0} contains an invalid manifest reference or it does not exist'.format(
                _TOSCA_METADATA_PATH))
            raise ToscaMalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

        # validate other tosca metadata
        for option in ToscaMetadataSchema._TOSCA_METADATA_OPTIONAL_KEYS:
            if option not in csar_metadata:
                logger.warning('Missing {0} option in {1}'.format(
                    option, _TOSCA_METADATA_PATH))

        # validate tosca manifest (yaml)
        with tempfile.TemporaryDirectory() as tmp_dir:
            unpack_archive(csar_path, tmp_dir)
            manifest_path = os.path.join(tmp_dir, manifest)
            validate_manifest(manifest_path)

        # replace ugly key with more user-friendly key for manifest filename
        csar_metadata['manifest_filename'] = csar_metadata.pop(_TOSCA_METADATA_MANIFEST_KEY)

    return csar_metadata
