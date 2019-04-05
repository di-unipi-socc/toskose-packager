class BaseToskerException(Exception):
    pass

class ToscaParsingError(BaseToskerException):
    """ Raised when the TOSCA .CSAR/.yml file does not exist """

    def __init__(self, message):
        super().__init__(message)

class ToscaValidationError(BaseToskerException):
    """ Raised when the TOSCA .CSAR/yml file is not valid """

    def __init__(self, message):
        super().__init__(message)