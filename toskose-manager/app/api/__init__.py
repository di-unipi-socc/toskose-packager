from flask import Blueprint
from flask_restplus import Api
from app.config import AppConfig


bp = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(
    bp,
    title='Toskose Manager API',
    version=AppConfig._APP_VERSION,
    description='API for managing TOSCA-based multi-component cloud applications'
)

# HTTP Error Handling
# TODO


from app.api.controllers.node_controller import ns as ns_node
api.add_namespace(ns_node, path='/node')

from app.api.controllers.subprocess_controller import ns as ns_subprocess
api.add_namespace(ns_subprocess, path='/subprocess')
