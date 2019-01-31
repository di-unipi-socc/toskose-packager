import os
import unittest

from flask_script import Manager

from app import create_app
from app.toskose_manager import ToskoseManager

application = create_app(os.environ.get('TOSKOSE_MANAGER_MODE') or 'dev')
application.app_context().push()

manager = Manager(application)


@manager.command
def run():

    application.run()


@manager.command
def test():
    """Runs unit tests"""

    tests = unittest.TestLoader().discover('../tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)

    if result.wasSuccessful():
        return 0
    return 1


if __name__ == "__main__":

    """ Load App Configuration

    ToskoseManager is initialized for the first time here, then it can be
    used overall the application environment by calling the singleton instance
    from the class.
    """
    tm = ToskoseManager()

    manager.run()
