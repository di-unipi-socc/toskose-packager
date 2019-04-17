import pytest
import tempfile

def test_temporary_filename():

    with tempfile.TemporaryDirectory() as tmp_dir:

        print(tmp_dir)