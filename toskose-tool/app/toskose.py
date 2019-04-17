import os

from app.common.logging import LoggingFacility
from app.common.exception import ToscaFatalError
from app.common.exception import ToscaFileNotFoundError
from app.common.exception import ToscaParsingError
from app.common.exception import ToscaValidationError
from app.common.commons import CommonErrorMessages
from app.tosca.loader import ToscaLoader
from app.tosca.validation.validator import ToscaValidator
from app.tosca.modeler import ToscaParser


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
                raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

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

        if debug: # override quiet
            LoggingFacility.get_instance().debug()

    @staticmethod
    def _build_output_dirs(output_path):
        """ """

        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
        except OSError as err:
            logger.error('Failed to create {0} directory'.format(output_path))
            logger.exception(err)
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
        else:
            logger.info('Output dir {0} built'.format(output_path))

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
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)

    @file_loader
    def generate(self, *args, **kwargs):
        """ """

        # Verify .CSAR archive
        if not self._is_csar:
            logger.error('A .CSAR archive must be loaded.')
            return

        logger.info('.CSAR successfully unpacked in {0}'.format(self._paths['csar_dir']))

        # Build output dir
        output_path = os.path.join(os.getcwd(), 'toskose_out')
        # user-defined output path
        if kwargs['output_path']:
            output_path = kwargs['output_path']

        Toskose._build_output_dirs(output_path)
        self._paths.update({'output_path': output_path})
        
        try:

            # Validation
            logger.info('Validating {0}..'.format(self._manifest_path))
            validated = ToscaValidator(self._manifest_path).validate()

            if not validated:
                logger.error('{0} is not valid.'.format(self._manifest_path))
                return
            
            logger.info('{0} validated.'.format(self._manifest_path))

            # Build Model
            logger.info('Parsing the TOSCA topology template..')
            tp = ToscaParser(self._manifest_path).build()

            logger.info('TOSCA topology template parsed.')

            # Build output dirs structure based on parsed template

            # Generate Supervisord configurations

            # 

        except ToscaValidationError as err:
            raise
        except OSError as err:
            logger.exception(err)
            raise ToscaFatalError(CommonErrorMessages._DEFAULT_FATAL_ERROR_MSG)
        except Exception as err:
            raise

        

            # gen supervisor conf..



        

        
