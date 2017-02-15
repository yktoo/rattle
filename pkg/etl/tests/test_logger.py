import os
import tempfile
import io
from etl import logger
from unittest.mock import patch


TEST_MSG = '**TEST MESSAGE**'


@patch('sys.stderr', new_callable=io.StringIO)
@patch('sys.stdout', new_callable=io.StringIO)
def _check_logger_std(severity, ignored, logging_func, mock_stdout, mock_stderr):
    """Output a specific message via logger to stdout/stderr and check its result."""
    global TEST_MSG
    # Run the logging function
    logging_func(TEST_MSG, severity)
    # Collect the output
    captured = mock_stdout.getvalue() if severity <= logger.INFO else mock_stderr.getvalue()
    print('Logger output: "' + captured + '"')
    # Check the output
    if ignored:
        # Output must be ignored, i.e. empty
        assert captured == ''
    else:
        # Output must contain the original message somewhere
        assert TEST_MSG in captured


def _check_logger_file(severity):
    """Output a specific message via logger to a file and check its result."""
    global TEST_MSG
    # Get a temp file name
    temp_handle, temp_file_name = tempfile.mkstemp()
    print('Temporary file used: ' + temp_file_name)
    try:
        # Close it right away
        os.close(temp_handle)

        # Log to the file and close it
        logger.set_log_file(temp_file_name)
        try:
            logger.log(TEST_MSG, severity)
        finally:
            logger.set_log_file(None)

        # The file must contain the original message somewhere
        with open(temp_file_name) as f:
            captured = f.read()
        print('Logger output: "' + captured + '"')
        assert TEST_MSG in captured

    finally:
        # Remove the file
        os.remove(temp_file_name)


def test_std_logging_verbose():
    """logger: test that in verbose mode all messages are output"""
    logger.set_log_file(None)
    logger.minimum_severity = logger.DEBUG
    _check_logger_std(logger.DEBUG,   False, logger.log)
    _check_logger_std(logger.INFO,    False, logger.log)
    _check_logger_std(logger.WARNING, False, logger.log)
    _check_logger_std(logger.ERROR,   False, logger.log)


def test_std_logging_debug_non_verbose():
    """logger: test that in non-verbose mode all messages except debug are output"""
    logger.set_log_file(None)
    logger.minimum_severity = logger.INFO
    _check_logger_std(logger.DEBUG,   True,  logger.log)
    _check_logger_std(logger.INFO,    False, logger.log)
    _check_logger_std(logger.WARNING, False, logger.log)
    _check_logger_std(logger.ERROR,   False, logger.log)


def test_std_logging_shorthand():
    """logger: test shorthand functions"""
    logger.set_log_file(None)
    logger.minimum_severity = logger.INFO
    _check_logger_std(logger.INFO,    False, lambda message, severity: logger.info(message))
    _check_logger_std(logger.WARNING, False, lambda message, severity: logger.warning(message))
    _check_logger_std(logger.ERROR,   False, lambda message, severity: logger.error(message))


def test_file_logging():
    """logger: test logging into file"""
    logger.minimum_severity = logger.INFO
    _check_logger_file(logger.INFO)


@patch('sys.stdout', new_callable=io.StringIO)
def test_separator(mock_stdout):
    """logger: test writing separator"""
    logger.separator()
    assert '=' * logger.output_width in mock_stdout.getvalue()
