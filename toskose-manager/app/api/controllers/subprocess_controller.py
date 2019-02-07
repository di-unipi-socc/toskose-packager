from flask_restplus import Resource, Namespace, fields, reqparse

from app.tosca.services.subprocess_service import SubProcessService

from app.tosca.models import ns_toskose_node as ns
from app.tosca.models import subprocess_info
from app.tosca.models import subprocess_multi_operation_result


@ns.header('Content-Type', 'application/json')
@ns.response(500, 'Operation failed')
@ns.response(404, 'Node not found')
@ns.response(200, 'Operation success')
class SubProcessOperation(Resource):
    """ Base class for common configurations """
    pass


parser_1 = reqparse.RequestParser() \
    .add_argument('signal', type=str, required=False,
        help='the signal to be sent (optional)')

@ns.route('/<string:node_id>/subprocess')
@ns.param('node_id', 'the node identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong url query \
    parameter')
class SubProcessList(SubProcessOperation):

    @ns.marshal_list_with(subprocess_info)
    def get(self, node_id):
        """ The list of subprocesses """
        return SubProcessService() \
            .get_all_subprocesses_info(node_id=node_id)

    @ns.expect(parser_1, validate=True)
    @ns.marshal_list_with(subprocess_multi_operation_result)
    def post(self, node_id):
        """ Start or signal all subprocesses """

        signal = parser_1.parse_args()['signal']
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

    @ns.expect(parser_1, validate=True)
    @ns.marshal_list_with(subprocess_multi_operation_result)
    def post(self, node_id, group_id):
        """ Start or signal all subprocesses in a group """

        signal = parser_1.parse_args()['signal']
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

    @ns.marshal_with(subprocess_info)
    def get(self, node_id, group_id, subprocess_id):
        """ Info about a subprocess """
        return SubProcessService() \
                .manage_subprocesses(
                    operation='info',
                    node_id=node_id,
                    group_id=group_id,
                    subprocess_id=subprocess_id)

    @ns.expect(parser_1, validate=True)
    def post(self, node_id, group_id, subprocess_id):
        """ Start or signal a subprocess """

        signal = parser_1.parse_args()['signal']
        if signal:
            res = SubProcessService() \
                .manage_subprocesses(
                    operation='start',
                    node_id=node_id,
                    group_id=group_id,
                    subprocess_id=subprocess_id,
                    is_signal=True,
                    signal=signal)

            return {'message': 'OK'} if res else \
                ns.abort(500, message='Failed to signal the subprocess')

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

""" Subprocess Logging """

@ns.route('/<string:node_id>/subprocess/logs-clear')
class SubProcessLogClearAll(Resource):

    @ns.marshal_with(subprocess_multi_operation_result)
    def post(self, node_id):
        """ Clear all subprocesses logs """
        return SubProcessService().manage_subprocess_log(
            operation='clear_all',
            node_id=node_id
        )

parser2 = reqparse.RequestParser() \
    .add_argument('std_type', type=str, required=True,
        help='the std we read from (stdout | stderr)') \
    .add_argument('offset', type=int, required=True,
        help='the offset (0 all the log)') \
    .add_argument('length', type=int, required=True,
        help='the length (0 all the log)')

@ns.param('node_id', 'the node identifier')
@ns.param('group_id', 'the subprocess\' group identifier')
@ns.param('subprocess_id', 'the subprocess identifier')
@ns.response(400, 'Operation failed, the cause may be a wrong group_id or \
    subprocess_id or a wrong url query parameter')
class SubProcessLog(SubProcessOperation):
    pass

@ns.route('/<string:node_id>/subprocess/<string:group_id>/\
<string:subprocess_id>/read-log')
class SubProcessLogRead(SubProcessLog):

    @ns.expect(parser2, validate=True)
    def get(self, node_id, group_id, subprocess_id):
        """ Read the log of a subprocess """
        log = SubProcessService().manage_subprocess_log(
            operation='read',
            std_type=parser2.parse_args()['std_type'],
            node_id=node_id,
            group_id=group_id,
            subprocess_id=subprocess_id,
            offset=parser2.parse_args()['offset'],
            length=parser2.parse_args()['length']
        )

        return log if log else ns.abort(500, message='failed to read log')

@ns.route('/<string:node_id>/subprocess/<string:group_id>/\
<string:subprocess_id>/tail-log')
class SubProcessLogTail(SubProcessLog):

    @ns.expect(parser2, validate=True)
    def get(self, node_id, group_id, subprocess_id):
        """ Tail the log of a subprocess """
        log = SubProcessService().manage_subprocess_log(
            operation='tail',
            std_type=parser2.parse_args()['std_type'],
            node_id=node_id,
            group_id=group_id,
            subprocess_id=subprocess_id,
            offset=parser2.parse_args()['offset'],
            length=parser2.parse_args()['length']
        )

        return log if log else ns.abort(500, message='failed to tail log')

@ns.route('/<string:node_id>/subprocess/<string:group_id>/\
<string:subprocess_id>/clear-log')
class SubProcessLogClear(SubProcessLog):

    @ns.expect(parser2, validate=True)
    def post(self, node_id, group_id, subprocess_id):
        """ Clear the log of a subprocess """
        res = SubProcessService().manage_subprocesses_log(
            operation='clear',
            node_id=node_id,
            group_id=group_id,
            subprocess_id=subprocess_id
        )

        return {'message': 'OK'} if res \
            else ns.abort(500, message='failed to clear log')
