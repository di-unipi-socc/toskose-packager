import os
import sys
import zipfile
from contextlib import contextmanager
from enum import Enum, auto
import getpass

_BASE_ERROR_MSG = 'See logs for further details.'


def unpack_archive(archive_path, output_path):

    with zipfile.ZipFile(archive_path, 'r') as archive:
        archive.extractall(output_path)

@contextmanager
def suppress_stderr():
    with open(os.devnull, "w") as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:  
            yield
        finally:
            sys.stderr = old_stderr   

def dict_recursive_lookup(dictionary, key, occ=[]):
    """ Search recursevely all the occurences of key, including eventually nested dicts """
    
    if isinstance(dictionary, dict):
        for k,v in dictionary.items():
            if k == key:
                occ.append(dictionary[key])
            else:
                dict_recursive_lookup(v, key, occ)


def create_auth(username, password):
    return {
        "username": username,
        "password": password
    }


def create_auth_interactive(user_text=None, pw_text=None):

    if user_text is None:
        user_text = ''
    if pw_text is None:
        pw_text = ''
    
    username = input(user_text)
    password = getpass.getpass(prompt=pw_text)
    return create_auth(username, password)


def create_input_with_dflt(text=None, dflt=None):

    if text is not None and dflt is not None:
        text = '{0} [ENTER for {1}]'.format(text, dflt)

    return input(text)


class Alerts(Enum):
    Success = auto()
    Warning = auto()
    Failure = auto()

class CommonErrorMessages:
    _DEFAULT_CONTAINER_RUNTIME_ERROR_MSG = 'An error is occurred during the communication with the container engine' + _BASE_ERROR_MSG
    _DEFAULT_SUPERVISORD_CONFIG_GEN_ERROR_MSG = 'An error is occurred during the Supervisord.conf generation. ' + _BASE_ERROR_MSG
    _DEFAULT_TRANSLATION_ERROR_MSG = 'An error is occurred during the translation. ' + _BASE_ERROR_MSG
    _DEFAULT_PARSING_ERROR_MSG = 'The TOSCA Manifest is invalid. ' + _BASE_ERROR_MSG
    _DEFAULT_FATAL_ERROR_MSG = 'A fatal error is occurred. ' + _BASE_ERROR_MSG 
    _DEFAULT_MALFORMED_CSAR_ERROR_MSG = 'The given CSAR archive is invalid. ' + _BASE_ERROR_MSG
    _DEFAULT_OPERATION_ABORTING_ERROR_MSG = 'Operation aborted by the user.'