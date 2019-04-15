import os
import sys
from contextlib import contextmanager
from enum import Enum, auto
from dataclasses import dataclass


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
