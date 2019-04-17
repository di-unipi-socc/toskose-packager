import os
import sys
import zipfile
from contextlib import contextmanager
from enum import Enum, auto
from dataclasses import dataclass


def unpack_archive(archive_path, output_path):

    with zipfile.ZipFile(archive_path, 'r') as archive:
        archive.extractall(output_path)

class Alerts(Enum):
    Success = auto()
    Warning = auto()
    Failure = auto()

@contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stderr = old_stderr   

class CommonErrorMessages:
    _DEFAULT_FATAL_ERROR_MSG = 'A fatal error is occurred. See logs for further details.' 
    _DEFAULT_MALFORMED_CSAR_ERROR_MSG = 'The given CSAR archive is invalid. See logs for further details.'