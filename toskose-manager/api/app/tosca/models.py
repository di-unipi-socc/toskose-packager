from flask_restplus import Namespace, fields
from dataclasses import dataclass, field
from typing import Dict

"""
Node Namespace
"""
ns_toskose_node = Namespace(
    'node',
    description='Operations for managing the nodes.'
)

"""
Node Schemas
"""
toskose_node = ns_toskose_node.model('ToskoseNode', {
    'id': fields.String(
        required=True,
        description='The node\'s identifier'
    ),
    'name': fields.String(
        required=True,
        description='The node\'s name'
    ),
    'description': fields.String(
        required=True,
        description='The node\'s description'
    ),
    'hostname': fields.String(
        required=True,
        description='The node\'s hostname'
    ),
    'port': fields.String(
        required=True,
        description='The node\'s port'
    ),
    'username': fields.String(
        required=True,
        description='The node\'s username'
    ),
    'password': fields.String(
        required=True,
        description='The node\'s password'
    )
})

toskose_node_info = ns_toskose_node.inherit('ToskoseNodeInfo', toskose_node, {

    'api_protocol': fields.String(
        required=True,
        description='The protocol used for communicating with the node API'
    ),
    'api_version': fields.String(
        required=True,
        description='The node API version'
    ),
    'supervisor_version': fields.String(
        required=True,
        description='The version of the hosted Supervisor instance'
    ),
    'supervisor_id': fields.String(
        required=True,
        description='The identifier of the hosted Supervisor instance'
    ),
    'supervisor_state': fields.Nested(ns_toskose_node.model('Data', {
        'name': fields.String(
            required=True,
            description='The name of the state'),
        'code': fields.String(
            required=True,
            description='The code of the state')
        }),
        required=True,
        description='The state of the hosted Supervisor instance'
    ),
    'supervisor_pid': fields.String(
        required=True,
        description='The PID of the supervisord process'
    ),
    'reacheable': fields.Boolean(
        required=True,
        description='A system message for reporting any errors occurred'
    )
})

toskose_node_log = ns_toskose_node.model('ToskoseNodeLog', {
    'log': fields.String(
        required=True,
        description='The log of the node'
    )
})

"""
Node DTO
"""

def default_supervisor_state():
    return {
        'name': 'No Data',
        'code': 'No Data'
    }

# https://realpython.com/python-data-classes/
# https://www.python.org/dev/peps/pep-0557/
@dataclass(frozen=True)
class ToskoseNodeInfoDTO:
    """ Info about a Toskose Node (DTO) """

    reacheable: bool
    id: str
    name: str
    description: str
    hostname: str
    port: str
    username: str
    password: str
    api_protocol: str
    api_version: str = 'No Data'
    supervisor_version: str = 'No Data'
    supervisor_id: str = 'No Data'
    supervisor_state: Dict = field(default_factory=default_supervisor_state)
    supervisor_pid: str = 'No Data'

@dataclass(frozen=True)
class ToskoseNodeLogDTO:
    """ The log of the node """

    log: str

"""
Subprocess Namespace
"""
ns_subprocess = Namespace(
    'subprocess',
    description='Operations for managing the subprocesses within the node.'
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

subprocess_single_operation_result = \
    ns_subprocess.model('SubprocessSingleOperationResult', {
        'message': fields.String(
            required=True,
            description='The result of the operation, True if successfull.'
        )
    })

subprocess_multi_operation_result = ns_subprocess.model('SubprocessOperationResult', {
    'name': fields.String(
        required=True,
        description='The name of the subprocess.'
    ),
    'group': fields.String(
        required=True,
        description='The name of the subprocess\'s group.'
    ),
    'status_code': fields.String(
        required=True,
        description='The status code returned for the operation.'
    ),
    'description': fields.String(
        required=True,
        description='A description about the operation\' result.'
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

@dataclass(frozen=True)
class SubprocessSingleOperationResultDTO:
    message: str

@dataclass(frozen=True)
class SubprocessOperationResultDTO:
    name: str
    group: str
    status_code: str
    description: str
