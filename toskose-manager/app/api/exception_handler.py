from app.api import api

from app.client.exceptions import SupervisordClientFatalError
from app.client.exceptions import SupervisordClientProtocolError
from app.client.exceptions import SupervisordClientFaultError
from app.client.exceptions import SupervisordClientConnectionError
from app.core.toskose_manager import MissingConfigurationDataError
from app.core.toskose_manager import ToskoseManager


class BaseError(Exception):
    pass

class GenericFatalError(BaseError):
    """ """

    def __init__(self, message):
        super().__init__(message)

class ResourceNotFoundError(BaseError):
    """ Raised when a resource cannot be found (e.g. node) """

    def __init__(self, message):
        super().__init__(message)

class ClientConnectionError(BaseError):
    """ Raised when a communication fails """

    def __init__(self, message):
        super().__init__(message)

class ClientOperationFailedError(BaseError):
    """ Raised when an operation made by the client fails """

    def __init__(self, message):
        super().__init__(message)

class ClientFatalError(BaseError):
    """ Raised when a fatal error occurred in the client """

    def __init__(self, message):
        super().__init__(message)

class OperationNotValid(BaseError):
    """ Raised when an invalid operation occurred """

    def __init__(self, message):
        super().__init__(message)


@api.errorhandler(GenericFatalError)
def handle_generic_fatal_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(ClientFatalError)
def handle_client_fatal_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(MissingConfigurationDataError)
def handle_client_missing_configuration_data(error):
    return ({ 'message': '{0}'.format(error) }, 404)

@api.errorhandler(ResourceNotFoundError)
def handle_client_connection_error(error):
    return ({ 'message': '{0}'.format(error) }, 400)

@api.errorhandler(ClientOperationFailedError)
def handle_client_protocol_error(error):
    return ({ 'message': '{0}'.format(error) }, 400)

@api.errorhandler(ClientConnectionError)
def handle_client_connection_error(error):
    return ({ 'message': '{0}'.format(error) }, 404)

@api.errorhandler(OperationNotValid)
def handle_operation_not_valid(error):
    return ({ 'message': '{0}'.format(error) }, 400)
