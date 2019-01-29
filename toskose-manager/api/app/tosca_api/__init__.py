from flask import Blueprint
from flask_restplus import Api

from .dto import ToskoseNodeDTO
from .dto import SoftwareNodeDTO


bp = Blueprint('tosca_api', __name__, url_prefix='/api/v1')

api = Api(
    bp,
    title='Toskose Manager API',
    version='1.0',
    description='API for managing TOSCA-based multi-component cloud applications'
)

api.add_namespace(ToskoseNodeDTO.api, path='/toskose-node')
api.add_namespace(SoftwareNodeDTO.api, path='/software-node')
