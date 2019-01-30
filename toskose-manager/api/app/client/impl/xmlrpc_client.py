from xmlrpc.client import ServerProxy, ProtocolError, Fault
from app.client.impl.base_client import BaseClient
from app.client.exceptions import SupervisordClientOperationError
import logging


class ToskoseXMLRPCclient(BaseClient):

    def _handling_failures(func):
        """ Handling connection errors or failures in RPC """

        def wrapper(self, *args, **kwargs):
            try:
                try:
                    return func(self, *args, **kwargs)
                except ConnectionRefusedError as err:
                    self.logger.error('Cannot establish a connection to http://{0}:{1}'.format(self._host, self._port))
                    raise
                except (ProtocolError, Fault) as err:
                    self.logger.error('TODO: Protocol or Fault error')
                    raise
                except OSError as err:
                    self.logger.error('OS error: {0}'.format(err))
                    raise
                except ValueError as err:
                    self.logger.error('Value error: {0}'.format(err))
                    raise
                except:
                    self.logger.error('Unexpected Error: ')
                    raise
            except:
                raise SupervisordClientOperationError(
                "A problem occurred while contacting the node {0}".format(self._node_id))

        return wrapper

    def __init__(self, **kwargs):
        super(ToskoseXMLRPCclient, self).__init__(**kwargs)
        self._rpc_endpoint = \
            ToskoseXMLRPCclient.build_rpc_endpoint(**kwargs)
        self._instance = self.build()

        self.logger = logging.getLogger(__class__.__name__)
        self.logger.info(__class__.__name__ + "logger started")

    @staticmethod
    def build_rpc_endpoint(host, port, username=None, password=None):
        """ Build the RPC endpoint """

        auth = ""
        if username is not None and password is not None:
            auth = "{username}:{password}@".format(username=username, password=password)

        return "http://{auth}{host}:{port}/RPC2".format(auth=auth, host=host, port=port)

    def build(self):
        """ Build a connection with the XML-RPC Server """

        return ServerProxy(self._rpc_endpoint)

    @_handling_failures
    def get_state(self):
        return self._instance.supervisor.getState()

    @_handling_failures
    def get_process_info(self, name):
        return self._instance.supervisor.getProcessInfo(name)
