from flask_restplus import Resource, Namespace, fields, reqparse

from tosca.services.subprocess_service import SubProcessService

from tosca.models import ns_toskose_node as ns
from tosca.models import subprocess_info
from tosca.models import subprocess_multi_operation_result

@ns.header('Content-Type', 'application/json')
class SubProcessOperation(Resource):
    """ Base class for common configurations """
    pass

@ns.route('/<string:node_id>/subprocess')
@ns.param('node_id', 'the node identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong url query \
    parameter')
class SubProcessList(SubProcessOperation):

    """ Parsing query url """
    parser = reqparse.RequestParser() \
        .add_argument('signal', type=str, required=False,
            help='the signal to be sent (optional)')

    @ns.marshal_list_with(subprocess_info)
    def get(self, node_id):
        """ The list of subprocesses """
        return SubProcessService() \
            .manage_subprocesses(
                operation='info_all',
                node_id=node_id)

    @ns.expect(parser, validate=True)
    @ns.marshal_list_with(subprocess_multi_operation_result)
    def post(self, node_id):
        """ Start or signal all subprocesses """

        signal = SubProcess.parser.parse_args()['signal']
        if signal:
            return SubProcessService() \
                .manage_subprocesses(
                    operation='info_all',
                    node_id=node_id,
                    is_signal=True,
                    signal=signal)

        return SubProcessService() \
                .manage_subprocesses(
                operation='start_all',
                node_id=node_id,
                wait=True)

    @ns.marshal_list_with(subprocess_multi_operation_result)
    def delete(self, node_id):
        """ Stop all subprocesses """
        return SubProcessService() \
                .manage_subprocesses(
                    operation='stop_all',
                    node_id=node_id,
                    wait=True)

@ns.route('/<string:node_id>/subprocess/<string:group_id>')
@ns.param('node_id', 'the node identifier')
@ns.param('group_id', 'the subprocess\' group identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class SubProcessGroup(SubProcessOperation):

    parser = reqparse.RequestParser() \
        .add_argument('signal', type=str, required=False,
            help='the signal to be sent (optional)')

    @ns.expect(parser, validate=True)
    @ns.marshal_list_with(subprocess_multi_operation_result)
    def post(self, node_id, group_id):
        """ Start or signal all subprocesses in a group """

        signal = SubProcess.parser.parse_args()['signal']
        if signal:
            return SubProcessService() \
                .manage_subprocesses(
                    operation='start_group',
                    node_id=node_id,
                    group_id=group_id,
                    is_signal=True,
                    signal=signal)

        return SubProcessService() \
                .manage_subprocesses(
                operation='start_group',
                node_id=node_id,
                group_id=group_id,
                wait=True)

    @ns.marshal_list_with(subprocess_multi_operation_result)
    def delete(self, node_id, group_id):
        """ Stop all subprocesses in a group """
        return SubProcessService() \
                .manage_subprocesses(
                    operation='stop_group',
                    node_id=node_id,
                    group_id=group_id,
                    wait=True)

@ns.route('/<string:node_id>/subprocess/<string:group_id>/<string:subprocess_id>')
@ns.param('node_id', 'the node identifier')
@ns.param('group_id', 'the subprocess\' group identifier')
@ns.param('subprocess_id', 'the subprocess identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class SubProcess(SubProcessOperation):

    parser = reqparse.RequestParser() \
        .add_argument('signal', type=str, required=False,
            help='the signal to be sent (optional)')

    @ns.marshal_with(subprocess_info)
    def get(self, node_id, group_id, subprocess_id):
        """ Info about a subprocess """
        return SubProcessService() \
                .manage_subprocesses(
                    operation='info',
                    node_id=node_id,
                    group_id=group_id,
                    subprocess_id=subprocess_id)

    @ns.expect(parser, validate=True)
    def post(self, node_id, group_id, subprocess_id):
        """ Start or signal a subprocess """

        signal = SubProcess.parser.parse_args()['signal']
        if signal:
            return SubProcessService() \
                .manage_subprocesses(
                    operation='start',
                    node_id=node_id,
                    group_id=group_id,
                    subprocess_id=subprocess_id,
                    is_signal=True,
                    signal=signal)

        res = SubProcessService() \
                .manage_subprocesses(
                    operation='start',
                    node_id=node_id,
                    group_id=group_id,
                    subprocess_id=subprocess_id,
                    wait=True)

        return {'message': 'OK'} if res \
            else ns.abort(500, message='failed to start')

    def delete(self, node_id, group_id, subprocess_id):
        """ Stop a subprocess """
        res = SubProcessService() \
                .manage_subprocesses(
                    operation='stop',
                    node_id=node_id,
                    group_id=group_id,
                    subprocess_id=subprocess_id,
                    wait=True)

        return {'message': 'OK'} if res \
            else ns.abort(500, message='failed to stop')

@ns.route('/<string:node_id>/subprocess/<string:group_id>/\
<string:subprocess_id>/read-log')
@ns.param('node_id', 'the node identifier')
@ns.param('group_id', 'the subprocess\' group identifier')
@ns.param('subprocess_id', 'the subprocess identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class SubProcessLogRead(Resource):

    parser = reqparse.RequestParser() \
        .add_argument('std_type', type=str, required=True,
            help='the std we read from (stdout | stderr)') \
        .add_argument('offset', type=int, required=True,
            help='the offset (0 all the log)') \
        .add_argument('length', type=int, required=True,
            help='the length (0 all the log)')

    @ns.expect(parser, validate=True)
    def get(self, node_id, group_id, subprocess_id):
        """ Read the log of a subprocess """
        log = SubProcessService().manage_subprocess_log(
            operation='read',
            std_type=SubProcessLogRead.parser.parse_args()['std_type'],
            node_id=node_id,
            group_id=group_id,
            subprocess_id=subprocess_id,
            offset=SubProcessLogRead.parser.parse_args()['offset'],
            length=SubProcessLogRead.parser.parse_args()['length']
        )

        return log if log else ns.abort(500, message='failed to read log')

class SubProcessLogTail(Resource):
    pass
