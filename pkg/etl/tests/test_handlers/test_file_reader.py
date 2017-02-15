from os import sep
from nose.tools import raises
from etl import config
from etl.handlers import file_reader


def test_existing():
    """handlers.file_reader: test reading existing file"""
    # Instantiate and run the handler against this very file
    h = file_reader.Handler()
    result = h.run(config.Config({
        'this_file':    __file__,
        'file_name':    '{this_file}',  # Also test parameter substitution
        'output_param': 'the_text'
    }))
    # Check for this text
    assert '=WHATEVER=' in result['the_text']


@raises(FileNotFoundError)
def test_nonexistent():
    """handlers.file_reader: test reading nonexistent file"""
    # Instantiate and run the handler against a nonexistent file
    h = file_reader.Handler()
    h.run(config.Config({
        'file_name': sep + '.NONEXISTENT.'
    }))
