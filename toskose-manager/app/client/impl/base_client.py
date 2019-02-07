from abc import ABC, abstractmethod
from typing import List, Dict

"""
Most of the documentation is derived from http://supervisord.org/api.html
"""


class BaseClient(ABC):

    def __init__(self, host, port, username=None, password=None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

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

    """ Supervisord Process Management """

    @abstractmethod
    def get_api_version(self) -> str:
        """ The version of the RPC API used by supervisord.

        Returns:
            api_vid: the string version identifier.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def get_supervisor_version(self) -> str:
        """ The version of the Supervisor package runned by the supervisord process.

        Returns:
            vid: the string version identifier.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def get_identification(self) -> str:
        """ The identifying string of Supervisor.

        This allows the client to identify the Supervisor instance with
        which it is communicating in the case of multiple instances.

        Returns:
            id: the string identifier.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def get_state(self) -> dict:
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

    @abstractmethod
    def get_pid(self) -> int:
        """ The PID of the supervisord process.

        Returns:
            pid: the PID of supervisord.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def read_log(self, offset: int, length: int) -> str:
        """ Read length bytes from the main log starting at offset.

        Args:
            offset (int): the offset to start reading from.
            length (int): the number of bytes to read from the log.

        Returns:
            log: It can either return the entire log, a number of characters
            from the tail of the log, or a slice of the log specified by the
            offset and length parameters.

        If the log is empty and the entire log is requested, an empty string
        is returned.
        If either offset or length is out of range, the fault BAD_ARGUMENTS
        will be returned.
        If the log cannot be read, this method will raise either the NO_FILE
        error if the file does not exist or the FAILED error if any other
        problem was encountered.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def clear_log(self) -> bool:
        """ Clear the main log.

        Returns:
            bool: always return True unless error.

        If the log cannot be cleared because the log file does not exist, the
        fault NO_FILE will be raised. If the log cannot be cleared for any
        other reason, the fault FAILED will be raised.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def shutdown(self) -> bool:
        """ Shut down the supervisor process.

        Returns:
            bool: always return True unless error.

        This method shuts down the Supervisor daemon. If any processes are
        running, they are automatically killed without warning. Unlike most
        other methods, if Supervisor is in the FATAL state, this method will
        still function.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def restart(self) -> bool:
        """ Restart the supervisor process.

        Returns:
            bool: always return True unless error.

        This method soft restarts the Supervisor daemon. If any processes are
        running, they are automatically killed without warning. Note that the
        actual UNIX process for Supervisor cannot restart; only Supervisor’s
        main program loop. This has the effect of resetting the internal states
        of Supervisor. Unlike most other methods, if Supervisor is in the FATAL
        state, this method will still function.

        """
        raise NotImplementedError("need to be implemented")

    """ Supervisord Subprocesses Management """

    @abstractmethod
    def get_process_info(self, name: str) -> Dict:
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
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def get_all_process_info(self) -> List:
        """ Get info about all processes.

        Returns:
            result: a list of process status results.

        Each element contains a dict, and this dict contains the exact same
        elements as the dict returned by getProcessInfo. If the process table
        is empty, an empty array is returned.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def start_process(self, name: str, wait: bool = True) -> bool:
        """ Start a process.

        Args:
            name (str): the process name (or group:name, or group:*).
            wait (bool): wait for process to be fully started.

        Returns:
            result: always return True unless error.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def start_all_processes(self, wait: bool = True) -> List:
        """ Start all processes listed in the configuration file.

        Args:
            wait (bool): wait for each process to be fully started.

        Returns:
            result: a list of process status info dicts.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def start_process_group(self, name: str, wait: bool = True) -> List:
        """ Start all processes in a group by the group name.

        Args:
            name (str): the group name.
            wait (bool): wait for each process to be fully started.

        Returns:
            result: a list of process status info dicts.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def stop_process(self, name: str, wait: bool = True) -> bool:
        """ Stop a process by name.

        Args:
            name (str): the name of the process to stop (or 'group:name').
            wait (bool): wait for the process to be fully stopped.

        Returns:
            result (bool): always return True unless error.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def stop_process_group(self, name: str, wait: bool = True) -> List:
        """ Stop al processes in a group by the group name.

        Args:
            name (str): the group name.
            wait (bool): wait for each process to be fully stopped.

        Returns:
            result: a list of process status info dicts.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def stop_all_processes(self, wait: bool = True) -> List:
        """ Stop all processes in the process list.

        Args:
            wait (bool): wait for each process to be fully stopped.

        Returns:
            result: a list of process status info dicts.

        """
        raise NotImplementedError("need to be implemented")

    @abstractmethod
    def signal_process(self, name: str, signal: str) -> bool:
        """ Send an arbitrary UNIX signal to the process named by name.

        Args:
            name (str): the name of the process to signal (or group:name).
            signal (str): the signal to send as name or number (e.g. HUP or 1).

        Returns:
            result (bool): always return True unless error.

        """
        pass

    @abstractmethod
    def signal_process_group(self, name: str, signal: str) -> List:
        """ Send a signal to all process in the group named by name.

        Args:
            name (str): the name of the group to signal.
            signal (str): the signal to send as name or number (e.g. HUP or 1).

        Returns:
            result: a list of process status info for each process in group.

        """
        pass

    @abstractmethod
    def signal_all_processes(self, signal: str) -> List:
        """ Send a signal to all processes in the process list.

        Args:
            signal (str): the signal to send as name or number (e.g. HUP or 1)

        Returns:
            result: a list of process status info for each process in list.

        """
        pass

    @abstractmethod
    def send_process_stdin(self, name: str, chars: str) -> bool:
        """ Send a string of chars to the stdin of the process name.

        Note: if non-7-bit data is sent (unicode) it is encoded to UTF-8 before
        being sent to the process' stdin. If chars is not a string or is not
        unicode, INCORRECT_PARAMETERS is raised. If the process is not in the
        state of RUNNING, then a NOT_RUNNING is raised. If the process' stdin
        cannot accept input (e.g. it was closed by the child process), NO_FILE
        is raised.

        Args:
            name (str): the name of the process to send to (or group:name).
            chars (str): the character data to send to the process.

        Returns:
            result (bool): always return True unless error.

        """
        pass

    @abstractmethod
    def send_remote_comm_event(self, type: str, data: str) -> bool:
        """ Send an event that will be received by event listener subprocesses
            subscribing to the RemoteCommunicationEvent.

        Args:
            type (str): the type key in the event header.
            data (str): the event body.

        Returns:
            result (bool): always return True unless error.

        """
        pass

    @abstractmethod
    def reload_config(self) -> List:
        """ Reload the configuration.

        Returns:
            result: a list of three lists. Each list contains names of process
            groups. In particular:
            - The added list: gives the process groups that have been added.
            - The changed list: gives the process groups whose contents have
            changed.
            - The removed list: gives the process groups that are no longer in
            the configuration.

        """
        pass

    @abstractmethod
    def add_process_group(self, name: str) -> bool:
        """ Update the config for a running process from the config file.

        Args:
            name (str): the name of the process group to add.

        Returns:
            result (bool): return True if successfull, False otherwise.

        """
        pass

    @abstractmethod
    def remove_process_group(self, name: str) -> bool:
        """ Remove a stopped process from the active configuration.

        Args:
            name (str): the name of the process group to remove.

        Returns:
            result (bool): return True is successfull, False otherwise.

        """
        pass

    """ Supervisord Subprocesses Logging Management """

    @abstractmethod
    def read_process_stdout_log(self, name: str, offset: int, length: int) -> str:
        """ Read length bytes from the process' stdout log starting at offset.

        Args:
            name (str): the name of the process (or group:name).
            offset (int): the offset to start reading from.
            length (int): the number of bytes to read from the log.

        Returns:
            result (str): the log read.

        """
        pass

    @abstractmethod
    def read_process_stderr_log(self, name: str, offset: int, length: int) -> str:
        """ Read length bytes from the process' stderr log starting at offset.

        Args:
            name (str): the name of the process (or group:name).
            offset (int): the offset to start reading from.
            length (int): the number of bytes to read from the log.

        Returns:
            result (str): the log read.

        """
        pass

    @abstractmethod
    def tail_process_stdout_log(self, name: str, offset: int, length: int) -> List:
        """ Provides a more efficient way to tail the (stdout) log than
        read_process_stdout_log(). Use read_process_stdout_log() to read chunks
        and tail_process_stdout_log() to tail.

        Note: Requests (length) bytes from the (name)’s log, starting at
        (offset). If the total log size is greater than (offset + length),
        the overflow flag is set and the (offset) is automatically increased
        to position the buffer at the end of the log. If less than (length)
        bytes are available, the maximum number of available bytes will be
        returned. (offset) returned is always the last offset in the log +1.

        Args:
            name (str): the name of the process (or group:name).
            offset (int): the offset to start reading from.
            length (int): the number of bytes to read from the log.

        Returns:
            result: a list contains [bytes (str), offset (int), overflow (bool)].

        """
        pass

    @abstractmethod
    def tail_process_stderr_log(self, name: str, offset: int, length: int) -> List:
        """ Provides a more efficient way to tail the (stderr) log than
        read_process_stderr_log(). Use read_process_stderr_log() to read chunks
        and tail_process_stderr_log() to tail.

        Note: Requests (length) bytes from the (name)’s log, starting at
        (offset). If the total log size is greater than (offset + length),
        the overflow flag is set and the (offset) is automatically increased
        to position the buffer at the end of the log. If less than (length)
        bytes are available, the maximum number of available bytes will be
        returned. (offset) returned is always the last offset in the log +1.

        Args:
            name (str): the name of the process (or group:name).
            offset (int): the offset to start reading from.
            length (int): the number of bytes to read from the log.

        Returns:
            result: a list contains [bytes (str), offset (int), overflow (bool)].

        """
        pass

    @abstractmethod
    def clear_process_log(self, name: str) -> bool:
        """ Clear the stdout and stderr logs for the named process and reopen them.

        Args:
            name (str): the name of the process (or group:name).

        Returns:
            result (bool): always True unless error.

        """
        pass

    @abstractmethod
    def clear_all_process_logs(self) -> List:
        """ Clear all process log files.

        Returns:
            result: a list of process status info.

        """
        pass

    """ Supervisord System Methods Management """

    @abstractmethod
    def list_methods(self) -> List:
        """ Return an array listing the available method names.

        Returns:
            result: a list of method names available (str).

        """
        pass

    @abstractmethod
    def method_help(self, name: str) -> str:
        """ Return a string showing the method’s documentation.

        Args:
            name (str): the name of the method.

        Returns:
            result (str): the documentation of the method name.

        """
        pass

    @abstractmethod
    def method_signature(self, name: str) -> List:
        """ Return an array describing the method signature in the form
        [rtype, ptype, ptype...] where rtype is the return data type of the
        method, and ptypes are the parameter data types that the method accepts
        in method argument order.

        Args:
            name (str): the name of the method.

        Returns:
            result: a list with the result.

        """
        pass

    @abstractmethod
    def multicall(self, calls: List) -> List:
        """ Process an array of calls, and return an array of results. Calls
        should be structs of the form {‘methodName’: string, ‘params’: array}.
        Each result will either be a single-item array containing the result
        value, or a struct of the form {‘faultCode’: int, ‘faultString’: string}.
        This is useful when you need to make lots of small calls without lots of
        round trips.

        Args:
            calls: an list of call requests.

        Returns:
            result: an array of results.

        """
        pass
