import os
from tempfile import mkstemp
from etl import config
from etl.handlers import file_writer


_MESSAGE_A = 'TEST_MESSAGE_A'
_MESSAGE_B = 'TEST_MESSAGE_B'
_temp_file_name = ''


def setup_module():
    global _temp_file_name
    # Create a temp file
    temp_handle, _temp_file_name = mkstemp()
    # Close it right away
    os.close(temp_handle)


def teardown_module():
    global _temp_file_name
    # Remove the file
    os.remove(_temp_file_name)


def test_overwrite():
    """handlers.file_writer: test overwriting file"""
    global _MESSAGE_A, _temp_file_name

    # Put some initial data in the file
    with open(_temp_file_name, 'w') as f:
        f.write('some_data')

    # Instantiate and run the handler
    h = file_writer.Handler()
    h.run(config.Config({
        'data':        _MESSAGE_A,
        'output_file': '{temp_file}',  # Also test parameter substitution
        'temp_file':   _temp_file_name
    }))

    # Check file contents
    with open(_temp_file_name) as f:
        assert f.read() == _MESSAGE_A


def test_append():
    """handlers.file_writer: test appending file"""
    global _MESSAGE_A, _MESSAGE_B, _temp_file_name

    # Instantiate and run the handler
    h = file_writer.Handler()
    h.run(config.Config({
        'input_param': 'the_text',  # Also test input parameter mapping
        'the_text':    _MESSAGE_B,
        'output_file': _temp_file_name,
        'append':      True
    }))

    # Check file contents
    with open(_temp_file_name) as f:
        assert f.read() == _MESSAGE_A + _MESSAGE_B
