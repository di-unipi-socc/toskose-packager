from flask import Blueprint
from flask_restplus import Api


bp = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    bp,
    title='Toskose Manager API',
    version='1.0',
    description='API for managing TOSCA-based multi-component cloud applications'
)

# HTTP Error Handling
# TODO


from app.tosca.controllers.toskose_node import ns as ns_toskose_node

api.add_namespace(ns_toskose_node, path='/node')
#api.add_namespace(SoftwareNodeDTO.api, path='/software-node')
