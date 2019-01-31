from flask_restplus import Resource, Namespace, fields, reqparse

from app.tosca.services.subprocess_service import SubProcessOperationService

from app.tosca.models import ns_subprocess as ns
from app.tosca.models import subprocess_info
from app.tosca.models import subprocess_single_operation_result
from app.tosca.models import subprocess_multi_operation_result

@ns.header('Content-Type', 'application/json')
class SubProcessOperation(Resource):
    """ Base class for common configurations """
    pass

@ns.route('/<string:node_id>/')
@ns.param('node_id', 'the node identifier')
class SubProcessList(SubProcessOperation):

    parser = reqparse.RequestParser() \
        .add_argument('signal', type=str, required=False,
            help='the signal to be sent')

    @ns.marshal_list_with(subprocess_info)
    def get(self, node_id):
        """ The list of subprocesses """
        return SubProcessOperationService(node_id=node_id) \
                .get_all_subprocesses_info()

    @ns.expect(parser, validate=True)
    @ns.marshal_list_with(subprocess_multi_operation_result)
    def post(self, node_id):
        """ Start or signal all subprocesses """

        signal = SubProcess.parser.parse_args()['signal']
        if signal:
            return SubProcessOperationService(node_id=node_id) \
                .signal_all_subprocesses(signal)

        return SubProcessOperationService(node_id=node_id) \
                .start_all_subprocesses(wait=True)

    @ns.marshal_list_with(subprocess_multi_operation_result)
    def delete(self, node_id):
        """ Stop all subprocesses """
        return SubProcessOperationService(node_id=node_id) \
                .stop_all_subprocesses(wait=True)

@ns.route('/<string:node_id>/<string:group_id>')
@ns.param('node_id', 'the node identifier')
@ns.param('group_id', 'the subprocess\' group identifier')
class SubProcessGroup(SubProcessOperation):

    parser = reqparse.RequestParser() \
        .add_argument('signal', type=str, required=False,
            help='the signal to be sent')

    @ns.expect(parser, validate=True)
    @ns.marshal_list_with(subprocess_multi_operation_result)
    def post(self, node_id, group_id):
        """ Start or signal all subprocesses in a group """

        signal = SubProcess.parser.parse_args()['signal']
        if signal:
            return SubProcessOperationService(node_id=node_id) \
                .signal_subprocess_group(group_id, signal)

        return SubProcessOperationService(node_id=node_id) \
                .start_subprocess_group(group_id, wait=True)

    @ns.marshal_list_with(subprocess_multi_operation_result)
    def delete(self, node_id, group_id):
        """ Stop all subprocesses in a group """
        return SubProcessOperationService(node_id==node_id) \
                .stop_subprocess_group(group_id, wait=True)

@ns.route('/<string:node_id>/<string:group_id>/<string:subprocess_id>')
@ns.param('node_id', 'the node identifier')
@ns.param('group_id', 'the subprocess\' group identifier')
@ns.param('subprocess_id', 'the subprocess identifier')
class SubProcess(SubProcessOperation):

    parser = reqparse.RequestParser() \
        .add_argument('signal', type=str, required=False,
            help='the signal to be sent')

    @ns.marshal_with(subprocess_info)
    @ns.response(500, 'Failed to retrieve info about the subprocess')
    def get(self, node_id, group_id, subprocess_id):
        """ Info about a subprocess """
        return SubProcessOperationService(node_id=node_id) \
                .get_subprocess_info(subprocess_id)

    @ns.expect(parser, validate=True)
    @ns.marshal_with(subprocess_single_operation_result)
    def post(self, node_id, group_id, subprocess_id):
        """ Start or signal a subprocess """

        signal = SubProcess.parser.parse_args()['signal']
        if signal:
            return SubProcessOperationService(node_id=node_id) \
                .signal_subprocess(subprocess_id, signal)

        return SubProcessOperationService(node_id=node_id) \
                .start_subprocess(subprocess_id, wait=True)

    @ns.marshal_with(subprocess_single_operation_result)
    def delete(self, node_id, group_id, subprocess_id):
        """ Stop a subprocess """
        return SubProcessOperationService(node_id=node_id) \
                .stop_subprocess(subprocess_id, wait=True)
