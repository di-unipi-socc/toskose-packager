import pytest

import os
import ruamel.yaml
import tests.commons as commons
import tests.helpers as helpers

from app.common.exception import ParsingError
from app.configurator import Configurator
from app.tosca.parser import ToscaParser


@pytest.mark.parametrize('data', commons.apps_data)
def test_data_load(data):
    
    cfg = Configurator()
    config = cfg.load(os.path.join(data['base_dir'], 'toskose.yml'))
    

@pytest.mark.parametrize('data', commons.apps_data)
def test_config_validation(data):
    pass

def test_data_load_not_exist():
    with pytest.raises(ValueError):
        Configurator().load('abcderfgh.yml')


@pytest.mark.parametrize('data', commons.apps_data)
def test_data_dump(data):
    pass