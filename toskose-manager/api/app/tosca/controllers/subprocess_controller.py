from flask_restplus import Resource, Namespace, fields, reqparse

from app.tosca.services.subprocess_service import SubProcessService

from app.tosca.models import ns_subprocess as ns
from app.tosca.models import subprocess_info

@ns.header('Content-Type', 'application/json')
class SubProcessOperation(Resource):
    """ Base class for common configurations """
    pass

@ns.route('/<string:node_id>/')
class SubProcessInfoList(SubProcessOperation):
    @ns.marshal_list_with(subprocess_info)
    @ns.response(500, 'Failed to retrieve subprocesses list')
    def get(self, node_id):
        """ The list of subprocesses """
        return SubProcessService(node_id=node_id).get_all_process_info()
