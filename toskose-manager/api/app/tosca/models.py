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
Toskose Node Namespace
"""
ns_toskose_node = Namespace(
    'toskose-node',
    description='operations for managing a toskose node'
)

"""
Schemas
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
DTOs
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
