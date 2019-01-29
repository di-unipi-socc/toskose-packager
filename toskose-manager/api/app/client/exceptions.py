class Error(Exception):
    """Base class for other exceptions"""
    pass

class SupervisordClientOperationError(Error):
    """Raised when the supervisord's client failed during an operation"""

    def __init__(self, message):
        super().__init__(message)
