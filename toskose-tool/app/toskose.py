from os import path

from app.common.logging import LoggingFacility
from app.common.exception import ToscaFatalError
from app.common.exception import ToscaFileNotFoundError
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError
from app.tosca.loader import ToscaLoader
from app.tosca.validator import ToscaValidator


logger = LoggingFacility.get_instance().get_logger()


class Toskose():

    def file_loader(func):
        """ decorator for loading the .csar archive """
        def wrapper(self, *args, **kwargs):

            try:

                tl = ToscaLoader(kwargs['file'])
                self._paths = tl.get_paths()
                self._csar_metadata = tl.csar_metadata
                self._manifest_path = tl.manifest_path
                self._is_csar = tl.is_csar

            except (ToscaFileNotFoundError, ToscaParsingError, ToscaValidationError) as err:
                raise
            except Exception as err:
                logger.exception(err)
                raise ToscaFatalError('A fatal error is occurred. See logs for further details.')

            return func(self, *args, **kwargs)

        return wrapper

    def __init__(self, debug=False, quiet=False):
        
        self._paths = None
        self._csar_metadata = None
        self._is_csar = False

        self._setup_logging(debug=debug, quiet=quiet)
    
    def _setup_logging(self, debug, quiet):
        
        if quiet:
            LoggingFacility.get_instance().quiet()

        if debug:
            LoggingFacility.get_instance().debug()

    @file_loader
    def validate(self, *args, **kwargs):
        """ Validate a .CSAR archive or a single yaml manifest. """
        
        try:

            logger.info('Validating {0}..'.format(self._manifest_path))

            return ToscaValidator(self._manifest_path).validate()

        except ToscaValidationError as err:
            raise
        except Exception as err:
            logger.exception(err)
            raise ToscaFatalError('A fatal error is occurred. See logs for further details.')

    @file_loader
    def generate(self, *args, **kwargs):
        """ """

        if not self._is_csar:
            logger.error('A .CSAR archive must be loaded.')
            return

        logger.info('.CSAR successfully unpacked in {0}'.format(self._paths['csar_dir']))

        try:

            logger.info('Validating {0}..'.format(self._manifest_path))
            validated = ToscaValidator(self._manifest_path).validate()

            if not validated:
                logger.error('{0} is not valid.'.format(self._manifest_path))
                return
            
            logger.info('{0} validated.'.format(self._manifest_path))

            



        except ToscaValidationError as err:
            raise

        
