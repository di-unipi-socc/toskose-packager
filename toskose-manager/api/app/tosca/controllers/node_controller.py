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
        """ The list of toskose nodes identifiers """
        return {'id': '1'} # TODO change

@ns.route('/<string:node_id>')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeInfo(ToskoseNodeOperation):
    @ns.marshal_with(toskose_node_info)
    @ns.response(404, 'Node not found')
    @ns.response(400, 'Node identifier not valid')
    def get(self, node_id):
        """ The current state of a node """
        # TODO validate the node_id
        info = ToskoseNodeService(node_id).get_node_info()
        if not info:
            ns.abort(404)
        else:
            return info

@ns.route('/<string:node_id>/log')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeLog(ToskoseNodeOperation):

    parser = reqparse.RequestParser()
    parser.add_argument('offset', type=int, required=True)
    parser.add_argument('length', type=int, required=True)

    @ns.marshal_with(toskose_node_log)
    @ns.expect(parser, validate=True)
    @ns.response(404, 'Log not found')
    @ns.response(400, 'Node identifier not valid')
    def get(self, node_id):
        """ The log of a node """
        # TODO validate the node_id
        args = ToskoseNodeLog.parser.parse_args()
        log = ToskoseNodeService(node_id).get_node_log(
            args['offset'],
            args['length'])
        if not log:
            ns.abort(404, message='No log for Toskose Node #{0}'.format(node_id))
        else:
            return log

@ns.route('/<string:node_id>/shutdown')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeShutdown(ToskoseNodeOperation):

    @ns.response(500, 'Failed to shutdown')
    @ns.response(400, 'Node identifier not valid')
    def post(self, node_id):
        """ Shutdown the node """
        # TODO validate the node_id
        res = ToskoseNodeService(node_id).shutdown()
        if not res:
            ns.abort(500, message='Failed to shutdown the node #{0}'.format(node_id))
        else:
            return {'message': 'OK'}

@ns.route('/<string:node_id>/restart')
@ns.param('node_id', 'the node identifier')
class ToskoseNodeRestart(ToskoseNodeOperation):

    @ns.response(500, 'Failed to restart')
    @ns.response(400, 'Node identifier not valid')
    def post(self, node_id):
        """ Restart the node """
        # TODO validate the node_id
        res = ToskoseNodeService(node_id).restart()
        if not res:
            ns.abort(500, message='Failed to restart the node #{0}'.format(node_id))
        else:
            return {'message': 'OK'}
