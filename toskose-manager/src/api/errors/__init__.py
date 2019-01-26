from flask import Blueprint

bp = Blueprint('errors', __name__, template_folder='templates')

# avoid circular dependencies
from api.errors import handlers
