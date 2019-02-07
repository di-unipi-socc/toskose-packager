import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, current_app
from .config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

db = SQLAlchemy()               # SQL ORM (SQLAlchemy)
migrate = Migrate()             # DB Migration (Schema Updates)
login = LoginManager()          # Login
login.login_view = 'auth.login' # force users to log in
login.login_message = _l('Please log in to access this page.')
mail = Mail()                   # Mail
bootstrap = Bootstrap()         # Style
moment = Moment()               # Datetime/Timezone
babel = Babel()                 # Language Translations


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # Blueprints
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from .errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    from .users import bp as users_bp
    app.register_blueprint(users_bp)

    # Logging
    if not app.debug and not app.testing:

        if Config.TOSKOSE_LOGS_PATH is None:
            if not os.path.exists('logs'):
                os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/toskose-manager.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('- Toskose Manager GUI started -')

    return app


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])
