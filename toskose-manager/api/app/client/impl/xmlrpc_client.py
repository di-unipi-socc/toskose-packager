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
                except ConnectionRefusedError as conn_err:
                    self.logger.error(
                        'Cannot establish a connection to http://{0}:{1}\n \
                        Error: {2}'.format(
                            self._host,
                            self._port,
                            conn_err))
                    raise
                except Fault as ferr:
                    self.logger.error('-- a Fault Error occurred -- \n \
                        - Error Code: {0}\n \
                        - Error Message: {1}'.format(
                            ferr.faultCode,
                            ferr.faultString))
                    raise
                except ProtocolError as perr:
                    self.logger.error('-- A Protocol Error occurred -- \n \
                        - URL: {0}\n \
                        - HTTP/HTTPS headers: {1}\n \
                        - Error Code: {2}\n \
                        - Error Message: {3}'.format(
                            perr.url,
                            perr.headers,
                            perr.errcode,
                            perr.errmsg))
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
                    "A problem occurred while contacting the node {0}:{1}".format(
                        self._host, self._port)
                )

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

    """ Supervisord Process Management """

    @_handling_failures
    def get_api_version(self):
        return self._instance.supervisor.getAPIVersion()

    @_handling_failures
    def get_supervisor_version(self):
        return self._instance.supervisor.getSupervisorVersion()

    @_handling_failures
    def get_identification(self):
        return self._instance.supervisor.getIdentification()

    @_handling_failures
    def get_state(self):
        return self._instance.supervisor.getState()

    @_handling_failures
    def get_pid(self):
        return self._instance.supervisor.getPID()

    @_handling_failures
    def read_log(self, offset, length):
        return self._instance.supervisor.readLog(offset,length)

    @_handling_failures
    def clear_log(self):
        return self._instance.supervisor.clearLog()

    @_handling_failures
    def shutdown(self):
        return self._instance.supervisor.shutdown()

    @_handling_failures
    def restart(self):
        return self._instance.supervisor.restart()

    """ Supervisord Subprocesses Management """

    @_handling_failures
    def get_process_info(self, name):
        return self._instance.supervisor.getProcessInfo(name)
