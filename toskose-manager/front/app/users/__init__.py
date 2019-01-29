from flask import Blueprint

bp = Blueprint('users', __name__, template_folder='templates')

from app.users import routes
