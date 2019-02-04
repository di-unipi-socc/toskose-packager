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


from app.tosca.controllers.node_controller import ns as ns_node
api.add_namespace(ns_node, path='/node')

from app.tosca.controllers.subprocess_controller import ns as ns_subprocess
api.add_namespace(ns_subprocess, path='/subprocess')
