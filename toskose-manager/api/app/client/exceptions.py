class Error(Exception):
    """ Base class for other exceptions. """
    pass

class SupervisordClientFatalError(Error):
    """ Raised when a fatal error occurred (e.g. OSError) """

    def __init__(self, message):
        super().__init__(message)
        

class SupervisordClientConnectionError(Error):
    """ Raised when a connection error occurred during the supervisord's client
    communication.
    """

    def __init__(self, message):
        super().__init__(message)

class SupervisordClientProtocolError(Error):
    """ Raised when an operation on the remote Supervisord' API failed, caused
    by protocol. """

    def __init__(self, message):
        super().__init__(message)

class SupervisordClientFaultError(Error):
    """ Raised when an operation on the remote Supervisord' API failed. """

    def __init__(self, message):
        super().__init__(message)
