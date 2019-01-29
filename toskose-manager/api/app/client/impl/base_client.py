from abc import ABC, abstractmethod
from typing import List, Dict

"""
Most of the documentation is derived from http://supervisord.org/api.html
"""


class BaseClient(ABC):

    def __init__(self, node_id, host, port, username=None, password=None):
        self._node_id = node_id
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    @property
    def node_id(self):
        return self._node_id

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    # Supervisord process Management
    #
    # @abstractmethod
    # def getAPIVersion(self) -> str:
    #     """ The version of the RPC API used by supervisord.
    #
    #     Returns:
    #         api_vid: the string version identifier.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def getSupervisorVersion(self) -> str:
    #     """ The version of the Supervisor package runned by the supervisord process.
    #
    #     Returns:
    #         vid: the string version identifier.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def getIdentification(self) -> str:
    #     """ The identifying string of Supervisor.
    #
    #     This allows the client to identify the Supervisor instance with
    #     which it is communicating in the case of multiple instances.
    #
    #     Returns:
    #         id: the string identifier.
    #
    #     """
    #     pass

    @abstractmethod
    def getState(self) -> Dict:
        """ The current state of Supervisor.

        Returns:
            state: A dict containing the code and the name of the current state
            of Supervisor. For example:

            {'statecode': 0,
            'statename': 'RESTARTING'}

            The possible return values are - NAME(CODE):
                - FATAL (2) - Supervisor has experienced a serious error
                - RUNNING (1) - Supervisor is working normally
                - RESTARTING (0) - Supervisor is in the process of restarting
                - SHUTDOWN (-1) - Supervisor is in the process of shutting down

        """
        raise NotImplementedError("not implemented yet")
    #
    # @abstractmethod
    # def getPid(self) -> int:
    #     """ The PID of the supervisord process.
    #
    #     Returns:
    #         pid: the PID of supervisord.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def readLog(self, offset: int, length: int) -> str:
    #     """ Read length bytes from the main log starting at offset.
    #
    #     Args:
    #         offset (int): the offset to start reading from.
    #         length (int): the number of bytes to read from the log.
    #
    #     Returns:
    #         log: It can either return the entire log, a number of characters
    #         from the tail of the log, or a slice of the log specified by the
    #         offset and length parameters.
    #
    #     If the log is empty and the entire log is requested, an empty string
    #     is returned.
    #     If either offset or length is out of range, the fault BAD_ARGUMENTS
    #     will be returned.
    #     If the log cannot be read, this method will raise either the NO_FILE
    #     error if the file does not exist or the FAILED error if any other
    #     problem was encountered.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def clearLog(self) -> bool:
    #     """ Clear the main log.
    #
    #     Returns:
    #         bool: always return True unless error.
    #
    #     If the log cannot be cleared because the log file does not exist, the
    #     fault NO_FILE will be raised. If the log cannot be cleared for any
    #     other reason, the fault FAILED will be raised.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def shutdown(self) -> bool:
    #     """ Shut down the supervisor process.
    #
    #     Returns:
    #         bool: always return True unless error.
    #
    #     This method shuts down the Supervisor daemon. If any processes are
    #     running, they are automatically killed without warning. Unlike most
    #     other methods, if Supervisor is in the FATAL state, this method will
    #     still function.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def restart(self) -> bool:
    #     """ Restart the supervisor process.
    #
    #     Returns:
    #         bool: always return True unless error.
    #
    #     This method soft restarts the Supervisor daemon. If any processes are
    #     running, they are automatically killed without warning. Note that the
    #     actual UNIX process for Supervisor cannot restart; only Supervisor’s
    #     main program loop. This has the effect of resetting the internal states
    #     of Supervisor. Unlike most other methods, if Supervisor is in the FATAL
    #     state, this method will still function.
    #
    #     """
    #     pass

    # Process Control

    @abstractmethod
    def getProcessInfo(self, name: str) -> Dict:
        """ Get info about a process by its name.

        Args:
            name (str): the name of the process or the group (e.g. group:name).

        Returns:
            info: a dict containing data about the process. For example:

            {'name':           'process name',
             'group':          'group name',
             'description':    'pid 18806, uptime 0:03:12'
             'start':          1200361776,
             'stop':           0,
             'now':            1200361812,
             'state':          20,
             'statename':      'RUNNING',
             'spawnerr':       '',
             'exitstatus':     0,
             'logfile':        '/path/to/stdout-log',
             'stdout_logfile': '/path/to/stdout-log',
             'stderr_logfile': '/path/to/stderr-log',
             'pid':            1}

        where:
            name (str): the name of the process.
            group (str): the name of the process's group.
            description (str): If process state is running description’s
                value is process_id and uptime. Example “pid 18806,
                uptime 0:03:12”. If process state is stopped description’s value
                is stop time. Example:”Jun 5 03:16 PM ”.
            start (long): the UNIX timestamp of when the process was started.
            stop (long): the UNIX timestamp of when the process last ended, or 0
                if the process has never been stopped.
            now (long): the UNIX timestamp of the current time, which can be
                used to calculate process up-time.
            state (int): the process state code.
            statename (str): the string description of the process state.
            logfile (str): deprecated (backward compatibility with Supervisor 2)
            stdout_logfile (str): Absolute path and filename to the STDOUT logfile.
            stderr_logfile (str): Absolute path and filename to the STDERR logfile.
            spawnerr (str): Description of error that occurred during spawn,
                or empty string if none.
            exitstatus (int): Exit status (errorlevel) of process, or 0 if the
                process is still running.
            pid (int): UNIX process ID (PID) of the process, or 0 if the process
                is not running.

        """
        raise NotImplementedError("not implemented yet")

    # @abstractmethod
    # def getAllProcessInfo(self) -> List:
    #     """ Get info about all processes.
    #
    #     Returns:
    #         result: a list of process status results.
    #
    #     Each element contains a dict, and this dict contains the exact same
    #     elements as the dict returned by getProcessInfo. If the process table
    #     is empty, an empty array is returned.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def startProcess(self, name: str, wait: bool = True) -> bool:
    #     """ Start a process.
    #
    #     Args:
    #         name (str): the process name (or group:name, or group:*).
    #         wait (bool): wait for process to be fully started.
    #
    #     Returns:
    #         result: always return True unless error.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def startAllProcesses(self, wait: bool = True) -> List:
    #     """ Start all processes listed in the configuration file.
    #
    #     Args:
    #         wait (bool): wait for each process to be fully started.
    #
    #     Returns:
    #         result: a list of process status info dicts.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def startProcessGroup(self, name: str, wait: bool = True) -> List:
    #     """ Start all processes in a group by the group name.
    #
    #     Args:
    #         name (str): the group name.
    #         wait (bool): wait for each process to be fully started.
    #
    #     Returns:
    #         result: a list of process status info dicts.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def stopProcess(self, name: str, wait: bool = True) -> bool:
    #     """ Stop a process by name.
    #
    #     Args:
    #         name (str): the name of the process to stop (or 'group:name').
    #         wait (bool): wait for the process to be fully stopped.
    #
    #     Returns:
    #         result (bool): always return True unless error.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def stopProcessGroup(self, name: str, wait: bool = True) -> List:
    #     """ Stop al processes in a group by the group name.
    #
    #     Args:
    #         name (str): the group name.
    #         wait (bool): wait for each process to be fully stopped.
    #
    #     Returns:
    #         result: a list of process status info dicts.
    #
    #     """
    #     pass
    #
    # @abstractmethod
    # def stopAllProcesses(self, wait: bool = True) -> List:
    #     """ Stop all processes in the process list.
    #
    #     Args:
    #         wait (bool): wait for each process to be fully stopped.
    #
    #     Returns:
    #         result: a list of process status info dicts.
    #     """
    #     pass
    #
    # @abstractmethod
    # def signalProcess(self, name, signal):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def signalProcessGroup(self, name, signal):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def signalAllProcesses(self, signal):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def sendProcessStdin(self, name, chars):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def sendRemoteCommEvent(self, type, data):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def reloadConfig(self):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def addProcessGroup(self, name):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def removeProcessGroup(self, name):
    #     """
    #     """
    #     pass
    #
    # # Process Logging
    #
    # @abstractmethod
    # def readProcessStdoutLog(self, name, offset, length):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def readProcessStderrLog(self, name, offset, length):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def tailProcessStdoutLog(self, name, offset, length):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def tailProcessStderrLog(self, name, offset, length):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def clearProcessLogs(self, name):
    #     """
    #     """
    #     pass
    #
    # @abstractmethod
    # def clearAllProcessLogs(self):
    #     """
    #     """
    #     pass
