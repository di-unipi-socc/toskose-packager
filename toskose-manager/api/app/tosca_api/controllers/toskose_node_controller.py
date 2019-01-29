from flask_restplus import Resource
from ..services.toskose_node_service import ToskoseNodeService
from ..services.toskose_node_service import nodes_id
from ..dto import ToskoseNodeDTO


api = ToskoseNodeDTO.api
_node_state = ToskoseNodeDTO.node_state
_nodes = ToskoseNodeDTO.nodes


# will be changed with a centralized data structure

# @api.route('/')
# class NodeList(Resource):

@api.route('/')
class NodeList(Resource):
    @api.doc('get the list of toskose nodes')
    @api.marshal_list_with(_nodes)
    def get(self):
        """"""
        return nodes_id

@api.route('/<node_id>')
@api.param('node_id', 'The node identifier')
@api.response(404, 'Node not found')
class NodeState(Resource):
    @api.doc('get the node state')
    @api.marshal_with(_node_state)
    def get(self, node_id):
        """ get the current state of a node by its node id """
        state = ToskoseNodeService(node_id).get_state()
        if not state:
            print('todo')
        else:
            return state

    # if node is None:
    #     # abort
