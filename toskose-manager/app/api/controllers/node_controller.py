from flask_restplus import Resource, Namespace, fields, reqparse

from app.tosca.services.node_service import NodeService

from app.tosca.models import ns_toskose_node as ns
from app.tosca.models import toskose_node_info


@ns.header('Content-Type', 'application/json')
@ns.response(500, 'Operation failed')
@ns.response(404, 'Node not found')
@ns.response(200, 'Operation success')
class NodeOperation(Resource):
    """ Base class for common configurations """
    pass

@ns.route('/')
class ToskoseNodeInfoList(NodeOperation):
    @ns.marshal_list_with(toskose_node_info)
    def get(self):
        """ The list of nodes info """
        return NodeService().get_all_nodes_info()

@ns.route('/<string:node_id>')
@ns.param('node_id', 'the node identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class ToskoseNodeInfo(NodeOperation):
    @ns.marshal_with(toskose_node_info)
    def get(self, node_id):
        """ The current state of a node """
        return NodeService().get_node_info(node_id=node_id)

parser = reqparse.RequestParser()
parser.add_argument('offset', type=int, required=True,
    help='the offset (0 all the log)')
parser.add_argument('length', type=int, required=True,
    help='the length (0 all the log)')

@ns.route('/<string:node_id>/log')
@ns.param('node_id', 'the node identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class ToskoseNodeLog(NodeOperation):

    @ns.expect(parser, validate=True)
    def get(self, node_id):
        """ get the log of a node """

        res = NodeService().get_node_log(
            node_id=node_id,
            offset=parser.parse_args()['offset'],
            length=parser.parse_args()['length'])
        return res if res else \
            ns.abort(500, message='Failed to read log')

    def delete(self, node_id):
        """ clear the log of a node """
        res = NodeService().clear_log(node_id=node_id)
        return {'message': 'OK'} if res else \
            ns.abort(500, message='Failed to clear log')

@ns.param('node_id', 'the node identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class NodeSystemOperation(NodeOperation):
    pass

@ns.route('/<string:node_id>/shutdown')
class ToskoseNodeShutdown(NodeSystemOperation):

    def post(self, node_id):
        """ Shutdown the node """
        res = NodeService().shutdown(node_id=node_id)
        return {'message': 'OK'} if res else \
            ns.abort(500, message='Failed to shutdown')

@ns.route('/<string:node_id>/restart')
class ToskoseNodeRestart(NodeSystemOperation):

    def post(self, node_id):
        """ Restart the node """
        res = NodeService().restart(node_id=node_id)
        return {'message': 'OK'} if res else \
            ns.abort(500, message='Failed to restart')
