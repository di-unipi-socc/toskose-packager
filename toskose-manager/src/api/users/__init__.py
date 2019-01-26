from flask import Blueprint

bp = Blueprint('users', __name__, template_folder='templates')

# avoid circular dependencies
from api.users import routes
