from flask_restplus import Resource, Namespace, fields, reqparse

from tosca.services.node_service import NodeService

from tosca.models import ns_toskose_node as ns
from tosca.models import toskose_node_info
from tosca.models import toskose_node_log


@ns.header('Content-Type', 'application/json')
class ToskoseNodeOperation(Resource):
    """ Base class for common configurations """
    pass

@ns.route('/')
class ToskoseNodeInfoList(ToskoseNodeOperation):
    @ns.marshal_list_with(toskose_node_info)
    @ns.response(500, 'Failed to retrieve nodes list')
    def get(self):
        """ The list of nodes info """
        return NodeService().get_all_nodes_info()

@ns.route('/<string:node_id>')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeInfo(ToskoseNodeOperation):
    @ns.marshal_with(toskose_node_info)
    @ns.response(404, 'Node not found')
    @ns.response(400, 'Node identifier not valid')
    def get(self, node_id):
        """ The current state of a node """
        return NodeService().get_node_info(node_id=node_id)

@ns.route('/<string:node_id>/log')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeLog(ToskoseNodeOperation):

    parser = reqparse.RequestParser()
    parser.add_argument('offset', type=int, required=True)
    parser.add_argument('length', type=int, required=True)

    @ns.marshal_with(toskose_node_log)
    @ns.expect(parser, validate=True)
    @ns.response(404, 'Log not found or node not found')
    @ns.response(400, 'Node identifier not valid')
    def get(self, node_id):
        """ get the log of a node """
        args = ToskoseNodeLog.parser.parse_args()
        log = NodeService().get_node_log(
            node_id=node_id,
            offset=args['offset'],
            length=args['length'])
        if not log:
            ns.abort(404, message='No log for node #{0}'.format(node_id))
        else:
            return log

    def delete(self, node_id):
        """ clear the log of a node """
        res = NodeService().clear_log(node_id=node_id)
        if not res:
            ns.abort(500, message='Failed to clear the log for node #{0} \
                '.format(node_id))
        else:
            return ({'message': 'OK'}, 200)

@ns.route('/<string:node_id>/shutdown')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeShutdown(ToskoseNodeOperation):

    @ns.response(500, 'Failed to shutdown')
    @ns.response(404, 'Node not found')
    @ns.response(400, 'Node identifier not valid')
    def post(self, node_id):
        """ Shutdown the node """
        res = NodeService().shutdown(node_id=node_id)
        if not res:
            ns.abort(500, message='Failed to shutdown the node #{0} \
                '.format(node_id))
        else:
            return ({'message': 'OK'}, 200)

@ns.route('/<string:node_id>/restart')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeRestart(ToskoseNodeOperation):

    @ns.response(500, 'Failed to restart')
    @ns.response(404, 'Node not found')
    @ns.response(400, 'Node identifier not valid')
    def post(self, node_id):
        """ Restart the node """
        # TODO validate the node_id
        res = NodeService().restart(node_id=node_id)
        if not res:
            ns.abort(500, message='Failed to restart the node #{0} \
                '.format(node_id))
        else:
            return ({'message': 'OK'}, 200)
