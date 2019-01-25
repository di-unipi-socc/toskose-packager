from flask import Flask
from api.config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap

import logging
from logging.handlers import RotatingFileHandler
import os

# Main App
app = Flask(__name__)
app.config.from_object(Config)

# SQL ORM (SQLAlchemy)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

# Login Manager
login = LoginManager(app)
login.login_view = 'login' #force users to log in

# Mail Manager
mail = Mail(app)

# Style Manager
bootstrap = Bootstrap(app)

# logging
if not app.debug:
    if Config.TOSKOSE_LOGS_PATH is None:
        if not os.path.exists('logs'):
            os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/toskose-manager.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('- Toskose Manager API started -')

# avoid circular dependencies
from api import routes, models, errors
