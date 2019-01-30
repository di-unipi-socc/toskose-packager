from flask_restplus import Resource, Namespace, fields
from app.tosca.services.toskose_node_service import ToskoseNodeService
from app.tosca.services.toskose_node_service import nodes_id


ns = Namespace('toskose/node', description='operations for managing a toskose node')

node_state = ns.model('node-state', {
    'name': fields.String(required=True, description='the name of the current state'),
    'code': fields.String(required=True, description="the code of the current state")
})
nodes = ns.model('nodes', {
    'id': fields.String(required=True, description='the toskose node identifier')
})

node_codes = {
    200: 'Success',
    400: 'Validation Error',
    401: 'Unauthorized',
    404: 'Not found',
    500: 'Internal Server Error'
}


@ns.route('/')
@ns.doc(
    headers={'Content-Type': 'application/json'},
    responses={401: 'Unauthorized', 500: 'Internal Server Error'}
)
class ToskoseNodeList(Resource):
    @ns.marshal_list_with(nodes)
    def get(self):
        """ The list of toskose nodes identifiers """
        return {'id': '1'}


@ns.route('/<node_id>')
@ns.doc(
    params={'node_id': 'The node identifier'},
    responses=node_codes
)
class ToskoseNodeState(Resource):
    @ns.marshal_with(node_state)
    def get(self, node_id):
        """ The current state of a node """
        state = ToskoseNodeService(node_id).get_state()
        if not state:
            ns.abort(404)
        else:
            return state

    # if node is None:
    #     # abort
