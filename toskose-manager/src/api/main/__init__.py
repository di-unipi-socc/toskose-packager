from flask import Blueprint

bp = Blueprint('main', __name__, template_folder='templates')

# avoid circular dependencies
from api.main import routes
