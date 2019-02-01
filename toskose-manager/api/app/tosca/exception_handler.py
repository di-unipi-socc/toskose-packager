from tosca import api

from client.exceptions import SupervisordClientFatalError
from client.exceptions import SupervisordClientConnectionError
from client.exceptions import SupervisordClientProtocolError
from client.exceptions import SupervisordClientFaultError


def client_handling_failures(func):
    """ decorator for handling client failures """

    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except SupervisordClientConnectionError as ex:
            print('todo')

    return wrapper

@api.errorhandler(SupervisordClientFatalError)
def handle_fatal_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(SupervisordClientConnectionError)
def handle_connection_error(error):
    return ({ 'message': '{0}. Node not found'.format(error) }, 404)

@api.errorhandler(SupervisordClientProtocolError)
def handle_protocol_error(error):
    return ({ 'message': '{0}'.format(error) }, 500)

@api.errorhandler(SupervisordClientFaultError)
def handle_fault_error(error):
    return ({ 'message': '{0}'.format(error) })
