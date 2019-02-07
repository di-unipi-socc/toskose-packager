from app.core.toskose_manager import ToskoseManager

from app.client.exceptions import SupervisordClientConnectionError
from app.client.exceptions import SupervisordClientFatalError
from app.client.exceptions import SupervisordClientProtocolError
from app.client.exceptions import SupervisordClientFaultError

from app.api.exception_handler import GenericFatalError
from app.api.exception_handler import ClientFatalError
from app.api.exception_handler import ClientOperationFailedError
from app.api.exception_handler import ClientConnectionError
from app.api.exception_handler import OperationNotValid


class BaseService():

    """ client decorators

    init_client() instantiates the client and check node\'s reachability.
    If the validate_connection argument is set to False, then it suppresses the
    SupervisordConnectionError, so it will not be catched by the api errorhandler,
    but a boolean istance attribute regarding the reachability (is_reacheable)
    is always stored.
    This strategy meets the requirements to give partial info about the nodes
    (e.g. get_node_info() in NodeService) without raise an exception to the api
    controller, even if the node is offline.
    If the validate_connection argument is set to True, then the client is
    triggered before the function calling, and a SupervisordConnectionError
    will be raised if the node is offline.

    """

    @classmethod
    def init_client(cls, validate_node=False, validate_connection=False):
        def decorator(func):
            def wrapper(self, *args, **kwargs):

                """ validate the node identifier """
                if validate_node:
                    node_id = kwargs.get('node_id')
                    if not ToskoseManager.get_instance().get_node_data(
                        node_id=node_id):
                        raise ResourceNotFoundError(
                            'node {0} not found'.format(node_id))

                """ get the client instance """
                node_id = kwargs.get('node_id')
                self._client = \
                    ToskoseManager.get_instance().get_node_client_instance(node_id)

                """ check the reachability of the node """
                self._is_reacheable = True
                try:
                    self._client.get_identification()
                except SupervisordClientConnectionError as conn_err:
                    self._is_reacheable = False

                """ client connection validation """
                if validate_connection:
                    if not self._is_reacheable:
                        node_id = kwargs.get('node_id')

                        raise ClientConnectionError(
                            'node {0} is offline'.format(node_id))

                try:
                    res = func(self, *args, **kwargs)
                except (SupervisordClientFaultError, SupervisordClientProtocolError) as err:
                    raise ClientOperationFailedError(err)
                except SupervisordClientFatalError as err:
                    raise ClientFatalError(err)
                except OperationNotValid:
                    raise
                except:
                    raise GenericFatalError('an unexpected error is occurred')

                return res

            return wrapper
        return decorator

    def __init__(self):
        pass
