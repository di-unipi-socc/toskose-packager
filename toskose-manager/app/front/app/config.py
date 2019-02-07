import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'life-is-too-short-for-malloc'

    # SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'toskose-manager-test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Logging
    TOSKOSE_LOGS_PATH = os.environ.get('TOSKOSE_LOG_PATH') or None

    # Mail
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = os.environ.get('MAIL_PORT') or 25
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['password-reset@toskose.io']

    # Language Translation
    LANGUAGES = ['en', 'it']
