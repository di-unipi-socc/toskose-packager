from app.common.logging import LoggingFacility


class BaseToskoseException(Exception):
    
    DEFAULT_MESSAGE = 'An unknown exception occurred'

    def __init__(self, message=DEFAULT_MESSAGE):
        self.message = message

    def __str__(self):
        return self.message

class FileNotFoundError(BaseToskoseException):
    """ Raised when the TOSCA .CSAR/.yml file does not exist """
    
    def __init__(self, message):
        super().__init__(message)

class MalformedCsarError(BaseToskoseException):
    """ Raised when a TOSCA .CSAR archive contains malformed data """

    def __init__(self, message):
        super().__init__(message)

class ParsingError(BaseToskoseException):
    """ Raised when the parsing of the TOSCA .CSAR/.yml file fails """

    def __init__(self, message):
        super().__init__(message)

class ValidationError(BaseToskoseException):
    """ Raised when the configuration file is not valid """

    def __init__(self, message):
        super().__init__(message)

class PartialValidationError(BaseToskoseException):
    """ Raised when the configuration file is partially valid. """

    def __init__(self, message):
        super().__init__(message)

class TranslationError(BaseToskoseException):
    """ Raised when an error occurred during the translation of a TOSCA application """

    def __init__(self, message):
        super().__init__(message)

class FatalError(BaseToskoseException):
    """ Raised when a fatal error is occurred """

    def __init__(self, message):
        super().__init__(message)

class SupervisordConfigGeneratorError(BaseToskoseException):
    """ Raised when an error occurred during supervisord config generator """

    def __init__(self, message):
        super().__init__(message)

class DockerOperationError(BaseToskoseException):
    """ Raised when an operation with the docker engine is failed """

    def __init__(self, message):
        super().__init__(message)

class DockerAuthenticationFailedError(BaseToskoseException):
    """ Raised when the authentication concerning Docker failed """

    def __init__(self, message):
        super().__init__(message)

class OperationAbortedByUser(BaseToskoseException):
    """ Raised when the user decides to abort an operation. """

    def __init__(self, message):
        super().__init__(message)

class AppContextGenerationError(BaseToskoseException):
    """ Raised when the app context generation failed. """

    def __init__(self, message):
        super().__init__(message)