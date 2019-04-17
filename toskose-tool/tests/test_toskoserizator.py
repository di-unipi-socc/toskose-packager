import pytest

from app.toskoserizator import Toskoserizator

def test_toskoserizator():

    csar_path = '/home/matteo/git/toskose/tests/data/thinking-app/thinking.csar'
    output_path = '/home/matteo/temp/bbb'

    try:

        t = Toskoserizator(csar_path, output_path)
        t.toskosed()

    except Exception as err:
        print(err)
        assert False
