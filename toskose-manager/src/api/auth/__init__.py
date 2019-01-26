from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates')

# avoid circular dependencies
from api.auth import routes
