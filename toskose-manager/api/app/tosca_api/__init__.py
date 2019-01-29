from flask import Blueprint
from flask_restplus import Api

from app.tosca_api.controllers.container_nodes import ns as ns_container_nodes
from app.tosca_api.controllers.software_nodes import ns as ns_software_nodes


bp = Blueprint('tosca_api', __name__, url_prefix='/api/v1')

api = Api(
    bp,
    title='Toskose Manager API',
    version='1.0',
    description='API for managing TOSCA-based multi-component cloud applications'
)

api.add_namespace(ns_container_nodes, path='/container-nodes')
api.add_namespace(ns_software_nodes, path='/software-nodes')
