import os
from pathlib import Path
import time
import datetime
import logging

from app.config import AppConfig


class LoggingFacility:
    """ A singleton containing the logging settings """

    __instance = None

    @staticmethod
    def get_instance():
        """ The static access method """

        if LoggingFacility.__instance == None:
            LoggingFacility()
        return LoggingFacility.__instance

    def __init__(self):

        if LoggingFacility.__instance != None:
            raise Exception('This is a singleton')
        else:
            LoggingFacility.__instance = self

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

        """ Formatter """
        self.formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
            # [in %(pathname)s:%(lineno)d]')

        """ Output path """
        logs_path = AppConfig._LOGS_PATH
        if not logs_path:
            """ logs path not set -- use default """
            logs_path = self.__create_default_log_path()

        if not os.path.exists(logs_path):
            sys.exit('failed to setup logging')

        now = datetime.datetime.now()
        logs_path = os.path.join(logs_path, ('log_' + now.strftime("%Y-%m-%d") + '.log'))

        """ File Handler """
        self._file_handler = logging.handlers.RotatingFileHandler(
            logs_path,
            maxBytes=10240,
            backupCount=10)

        self._file_handler.setFormatter(self.formatter)
        self._file_handler.setLevel(logging.INFO)

        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(self.formatter)

        self._logger.addHandler(self._file_handler)
        self._logger.addHandler(streamHandler)

    def __create_default_log_path(self):

        base_dir = Path(__file__).parent.parent.parent
        logs_path = os.path.join(base_dir.resolve(), 'logs/')
        if not os.path.exists(logs_path):
            os.mkdir(logs_path)

        return logs_path

    def get_logger(self):
        return self._logger

    def get_handler(self):
        return self._file_handler
