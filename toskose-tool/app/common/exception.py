from app.common.logging import LoggingFacility


class BaseToskoseException(Exception):
    
    _message = 'An unknown exception occurred'

    def __init__(self, message=_message):
        self.message = message

    def __str__(self):
        return self.message

class ToscaFileNotFoundError(BaseToskoseException):
    """ Raised when the TOSCA .CSAR/.yml file does not exist """
    
    def __init__(self, message):
        super().__init__(message)

class ToscaParsingError(BaseToskoseException):
    """ Raised when the parsing of the TOSCA .CSAR/.yml file fails """

    def __init__(self, message):
        super().__init__(message)

class ToscaValidationError(BaseToskoseException):
    """ Raised when the TOSCA .CSAR/yml file is not valid """

    def __init__(self, message):
        super().__init__(message)