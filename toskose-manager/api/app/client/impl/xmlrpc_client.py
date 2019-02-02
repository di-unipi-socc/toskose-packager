from xmlrpc.client import ServerProxy, ProtocolError, Fault
from client.impl.base_client import BaseClient
from client.exceptions import SupervisordClientFatalError
from client.exceptions import SupervisordClientConnectionError
from client.exceptions import SupervisordClientProtocolError
from client.exceptions import SupervisordClientFaultError

import logging
from enum import Enum, auto


class ErrorType(Enum):
    FAULT = auto()


def error_messages_builder(type, error, *args):
    """ Build error messages """

    err = 'ERROR - '
    if type == ErrorType.FAULT:
        if error.faultCode == 70:
            """ NOT RUNNING """
            err += 'Process {0} not running'.format(args[0])
        elif error.faultCode == 60:
            """ ALREADY STARTED """
            err += 'Process {0} is already started'.format(args[0])
        elif error.faultCode == 10:
            """ BAD NAME """
            err += 'Process or group {0} not exist'.format(args[0])
        else:
            """ UNKNOWN """
            err += 'An Unknown error occurred'
    return err

class ToskoseXMLRPCclient(BaseClient):

    def _handling_failures(func):
        """ Handling connection errors or failures in RPC """

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ConnectionRefusedError as conn_err:
                self.logger.error(
                    'Cannot establish a connection to http://{0}:{1}\n \
                    Error: {2}'.format(
                        self._host,
                        self._port,
                        conn_err))
                raise SupervisordClientConnectionError(
                    "A problem occurred while contacting the node",
                    host=self._host,
                    port=self._port)

            except Fault as ferr:
                self.logger.error('-- a Fault Error occurred -- \n \
                    - Error Code: {0}\n \
                    - Error Message: {1}'.format(
                        ferr.faultCode,
                        ferr.faultString))
                raise SupervisordClientFaultError(
                    error_messages_builder(
                        ErrorType.FAULT,
                        ferr,
                        *args
                    ))

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
                raise SupervisordClientProtocolError('A protocol error occurred')

            except OSError as err:
                self.logger.error('OS error: {0}'.format(err))
                raise SupervisordClientFatalError('A fatal error occurred')

            except ValueError as err:
                self.logger.error('Value error: {0}'.format(err))
                raise SupervisordClientFatalError('A fatal error occurred')
            except:
                self.logger.error('Unexpected Error: ')
                raise SupervisordClientFatalError('A fatal error occurred')

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

    @_handling_failures
    def get_all_process_info(self):
        return self._instance.supervisor.getAllProcessInfo()

    @_handling_failures
    def start_process(self, name, wait):
        return self._instance.supervisor.startProcess(name,wait)

    @_handling_failures
    def start_all_processes(self, wait):
        return self._instance.supervisor.startAllProcesses(wait)

    @_handling_failures
    def start_process_group(self, name, wait):
        return self._instance.supervisor.startProcessGroup(name,wait)

    @_handling_failures
    def stop_process(self, name, wait):
        return self._instance.supervisor.stopProcess(name,wait)

    @_handling_failures
    def stop_process_group(self, name, wait):
        return self._instance.supervisor.stopProcessGroup(name,wait)

    @_handling_failures
    def stop_all_processes(self, wait):
        return self._instance.supervisor.stopAllProcesses(wait)

    @_handling_failures
    def signal_process(self, name, signal):
        return self._instance.supervisor.signalProcess(name,signal)

    @_handling_failures
    def signal_process_group(self, name, signal):
        return self._instance.supervisor.signalProcessGroup(name,signal)

    @_handling_failures
    def signal_all_processes(self, signal):
        return self._instance.supervisor.signalAllProcesses(signal)

    def send_process_stdin(self, name, chars):
        """ not implemented yet """
        pass

    def send_remote_comm_event(self, type, data):
        """ not implemented yet """
        pass

    @_handling_failures
    def reload_config(self):
        return self._instance.supervisor.reloadConfig()

    @_handling_failures
    def add_process_group(self, name):
        return self._instance.supervisor.addProcessGroup(name)

    @_handling_failures
    def remove_process_group(self, name):
        return self._instance.supervisor.removeProcessGroup(name)

    """ Supervisord Subprocesses Logging Management """

    @_handling_failures
    def read_process_stdout_log(self, name, offset, length):
        return self._instance.supervisor.readProcessStdoutLog(name,offset,length)

    @_handling_failures
    def read_process_stderr_log(self, name, offset, length):
        return self._instance.supervisor.readProcessStderrLog(name,offset,length)

    @_handling_failures
    def tail_process_stdout_log(self, name, offset, length):
        return self._instance.supervisor.tailProcessStdoutLog(name,offset,length)

    @_handling_failures
    def tail_process_stderr_log(self, name, offset, length):
        return self._instance.supervisor.tailProcessStderrLog(name,offset,length)

    @_handling_failures
    def clear_process_log(self, name):
        return self._instance.supervisor.clearProcessLogs(name)

    @_handling_failures
    def clear_all_process_logs(self):
        return self._instance.supervisor.clearAllProcessLogs()

    """ Supervisord System Methods Management """

    def list_methods(self):
        """ not implemented yet """
        pass

    def method_help(self, name):
        """ not implemented yet """
        pass

    def method_signature(self, name):
        """ not implemented yet """
        pass

    def multicall(self, calls):
        """ not implemented yet """
        pass
