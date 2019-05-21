import os
import tempfile
import zipfile
import yaml

from toscaparser.tosca_template import ToscaTemplate
from app.common.logging import LoggingFacility
from app.common.commons import unpack_archive
from app.common.commons import CommonErrorMessages
from app.common.commons import suppress_stderr
from app.common.exception import FileNotFoundError
from app.common.exception import ValidationError
from app.common.exception import MalformedCsarError
from app.common.exception import FatalError


logger = LoggingFacility.get_instance().get_logger()

_CSAR_ADMITTED_EXTENSIONS = (".zip", ".csar")

_TOSCA_METADATA_PATH = 'TOSCA-Metadata/TOSCA.meta'
_TOSCA_METADATA_OPTIONAL_KEYS = ['Created-By', 'CSAR-version', 'Description']
_TOSCA_METADATA_REQUIRED_KEYS = ['Entry-Definitions']
_TOSCA_METADATA_MANIFEST_KEY = 'Entry-Definitions'

_required_attrs = [
    "topology_template",
    "nodetemplates",
]

def _validate_manifest(manifest_path):
    pass


def validate_csar(csar_path):
    """ Validate a TOSCA-based application compressed in a .CSAR archive. """

    # file existence
    if not os.path.isfile(csar_path):
        err_msg = 'Missing .CSAR archive file'
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    # file extension
    if not csar_path.lower().endswith(_CSAR_ADMITTED_EXTENSIONS):
        _, ext = os.path.splitext(csar_path)
        err_msg = '{0} is an invalid file extension'.format(ext) \
            if ext \
            else 'file extension is not recognized'
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    # validate archive file
    if not zipfile.is_zipfile(csar_path):
        err_msg = '{0} is an invalid or corrupted archive'.format(csar_path)
        logger.error(err_msg)
        raise FileNotFoundError(err_msg)

    logger.debug('Validating [{}]'.format(csar_path))
    csar_metadata = {}

    # validate csar structure
    with zipfile.ZipFile(csar_path, 'r') as archive:
        with suppress_stderr(): #TODO fix yaml error and remove it (workaround)
            filelist = [e.filename for e in archive.filelist]

            if _TOSCA_METADATA_PATH not in filelist:
                logger.error('{0} does not contain a valid TOSCA.meta'.format(csar_path))
                raise MalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

            # validate TOSCA.meta
            try:

                #TODO !!!fix!!! YAMLLoadWarning: calling yaml.load() without Loader=... is deprecated, as the default Loader is unsafe. 
                # Please read https://msg.pyyaml.org/load for full details.
                csar_metadata = yaml.load(archive.read(_TOSCA_METADATA_PATH))
                if type(csar_metadata) is not dict:
                    logger.error('{0} is not a valid dictionary'.format(
                        _TOSCA_METADATA_PATH))
                    raise MalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

            except yaml.YAMLError as err:
                logger.exception(err)
                raise FatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

            # validate tosca metadata
            for key in _TOSCA_METADATA_REQUIRED_KEYS:
                if key not in csar_metadata:
                    logger.error('Missing {0} in {1}'.format(key, _TOSCA_METADATA_PATH))
                    raise MalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

            # validate tosca manifest file
            manifest = csar_metadata.get(_TOSCA_METADATA_MANIFEST_KEY)
            if manifest is None or manifest not in filelist:
                logger.error('{0} contains an invalid manifest reference or it does not exist'.format(
                    _TOSCA_METADATA_PATH))
                raise MalformedCsarError(CommonErrorMessages._DEFAULT_MALFORMED_CSAR_ERROR_MSG)

            # validate other tosca metadata
            for option in _TOSCA_METADATA_OPTIONAL_KEYS:
                if option not in csar_metadata:
                    logger.warning('Missing {0} option in {1}'.format(
                        option, _TOSCA_METADATA_PATH))

            # validate tosca manifest (yaml)
            with tempfile.TemporaryDirectory() as tmp_dir:
                unpack_archive(csar_path, tmp_dir)
                manifest_path = os.path.join(tmp_dir, manifest)
                _validate_manifest(manifest_path)

    return csar_metadata
