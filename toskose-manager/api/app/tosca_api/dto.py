from flask_restplus import Namespace, fields


class ToskoseNodeDTO:
    api = Namespace('toskose-node', description='operations for managing a toskose node')
    node_state = api.model('node-state', {
        'name': fields.String(required=True, description='the name of the current state'),
        'code': fields.String(required=True, description="the code of the current state")
    })
    nodes = api.model('nodes', {
        'id': fields.String(required=True, description='the toskose node identifier')
    })


class SoftwareNodeDTO:
    api = Namespace('software-node', description='operations for managing a software node')
    # TODO
