from flask_restplus import Namespace, fields
from dataclasses import dataclass
from typing import Dict


class ToskoseNode:
    """ A Toskose Node (internal representation) """
    def __init__(self, id, host, port, username, password):
        self._id = id
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    @property
    def id(self):
        return self._id

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

node_codes = {
    200: 'Success',
    400: 'Validation Error',
    401: 'Unauthorized',
    404: 'Not found',
    500: 'Internal Server Error'
}

"""
Node Namespace
"""
ns_toskose_node = Namespace(
    'node',
    description='operations for managing a toskose node'
)

"""
Node Schemas
"""
toskose_node_info = ns_toskose_node.model('ToskoseNodeInfo', {
    'id': fields.String(
        required=True,
        description='the identifier of the node'
    ),
    'host': fields.String(
        required=True,
        description='the hostname'
    ),
    'port': fields.String(
        required=True,
        description='the port'
    ),
    'api_protocol': fields.String(
        required=True,
        description='the protocol used for communicating with the node API'
    ),
    'api_version': fields.String(
        required=True,
        description='the node API version'
    ),
    'supervisor_version': fields.String(
        required=True,
        description='the version of the hosted Supervisor instance'
    ),
    'supervisor_id': fields.String(
        required=True,
        description='the identifier of the hosted Supervisor instance'
    ),
    'supervisor_state': fields.Nested(ns_toskose_node.model('Data', {
        'name': fields.String(
            required=True,
            description='the name of the state'),
        'code': fields.String(
            required=True,
            description='the code of the state')
        }),
        required=True,
        description='the state of the hosted Supervisor instance'
    ),
    'supervisor_pid': fields.String(
        required=True,
        description='the PID of the supervisord process'
    ),
})

toskose_node_log = ns_toskose_node.model('ToskoseNodeLog', {
    'log': fields.String(
        required=True,
        description='the log of the node'
    )
})

"""
Node DTO
"""

# https://realpython.com/python-data-classes/
# https://www.python.org/dev/peps/pep-0557/
@dataclass(frozen=True)
class ToskoseNodeInfoDTO:
    """ Info about a Toskose Node (DTO) """

    id: str
    host: str
    port: str
    api_protocol: str
    api_version: str
    supervisor_version: str
    supervisor_id: str
    supervisor_state: Dict
    supervisor_pid: str

@dataclass(frozen=True)
class ToskoseNodeLogDTO:
    """ The log of the node """

    log: str

"""
Subprocess Namespace
"""
ns_subprocess = Namespace(
    'subprocess',
    description='Operations for managing a subprocesses within the node.'
)

"""
Subprocess Schema
"""
subprocess_info = ns_subprocess.model('SubprocessInfo', {
    'name': fields.String(
        required=True,
        description='The name of the subprocess.'
    ),
    'group': fields.String(
        required=True,
        description='The name of the subprocess\'s group.'
    ),
    'description': fields.String(
        required=True,
        description='A description about the current state of the subprocess. \
        If the state is RUNNING, then process_id and the uptime is shown. \
        If the state is STOPPED, then the stop time is shown (e.g. Jun 5 03:16 PM). \
        Otherwise, a generic description about the state is shown (e.g. Not Started).'
    ),
    'time_start': fields.String(
        required=True,
        description='the timestamp of when the subprocess was started or 0 if \
        the subprocess has never beeen started.'
    ),
    'time_end': fields.String(
        required=True,
        description='The timestamp of when the subprocess last endend or 0 if \
        the subprocess has never been stopped.'
    ),
    'uptime': fields.String(
        required=True,
        description='The uptime of the subprocess or 0 if the subprocess has \
        never been started.'
    ),
    'state_code': fields.String(
        required=True,
        description='The code of the state of the subprocess. The possible codes are: \n \
        - 0: STOPPED \n \
        - 10: STARTING \n \
        - 20: RUNNING \n \
        - 30: BACKOFF \n \
        - 40: STOPPING \n \
        - 100: EXITED \n \
        - 200: FATAL \n \
        - 1000: UNKNOWN'
    ),
    'state_name': fields.String(
        required=True,
        description='The state of the subprocess. The possible states are: \n \
        - STOPPED: The subprocess has been stopped due to a stop request or has \
        never been started. \n \
        - STARTING: The subprocess is starting due to a start request. \n \
        - RUNNING: The subprocess is running. \n \
        - BACKOFF: The subprocess entered the STARTING state but subsequently \
        exited too quickly to move to the RUNNING state. \n \
        - STOPPING: The subprocess is stopping due to a stop request. \n \
        - EXITED: The subprocess exited from the RUNNING state (expectedly or \
        unexpectedly). \n \
        - FATAL: The subprocess could not be started successfully. \n \
        - UNKNOWN: The subprocess is in an unknown state.'
    ),
    'logfile_path': fields.String(
        required=False,
        description='Alias for stdout_logfile_path. Only for Supervisor 2.x \
        compatibility. (Deprecated)'
    ),
    'stdout_logfile_path': fields.String(
        required=True,
        description='The absolute path and the filename of the STDOUT logfile'
    ),
    'stderr_logfile_path': fields.String(
        required=True,
        description='The absolute path and the filename of the STDERR logfile. \
        It can be empty if the stderr redirection option is activated.'
    ),
    'spawn_error': fields.String(
        required=True,
        description='The description of the error that occurred during spawn or \
        an empty string if none error occurred.'
    ),
    'exit_status': fields.String(
        required=True,
        description='The exit status of the subprocess (ERROR LEVEL) or 0 if \
        the process is still running.'
    ),
    'pid': fields.String(
        required=True,
        description='The UNIX Process ID (PID) of the subprocess or 0 if the \
        subprocess is not running.'
    )
})

"""
Subprocess DTO
"""
@dataclass(frozen=True)
class SubprocessInfoDTO:
    name: str
    group: str
    description: str
    time_start: str
    time_end: str
    uptime: str
    state_code: str
    state_name: str
    logfile_path: str
    stdout_logfile_path: str
    stderr_logfile_path: str
    spawn_error: str
    exit_status: str
    pid: str
