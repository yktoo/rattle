"""
Generic logger implementation. Dumps messages to a file or the standard output/error, depending on settings and message
severity.
"""

import sys
import datetime
import atexit

# Message severities
DEBUG   = 0
INFO    = 1
WARNING = 2
ERROR   = 3

# Minimum severity of the messages printed out by the logger.
minimum_severity = INFO

# Output width  (currently only affects separators)
output_width = 80

# Log file object. If None, all the output goes to stdout/stderr.
_log_file = None


def _teardown():
    """Cleanup procedure for the module."""
    global _log_file
    # Close the log file, if any
    if _log_file is not None:
        _log_file.close()


def _write_line(line: str, stderr: bool):
    """Write a line to the log.
    :param line: Line to write to the log.
    :param stderr: Whether it's a critical message (warning or error) to be output to stderr instead of regular output.
    """
    # Add a linebreak
    line += '\n'
    # Output the text
    if _log_file is not None:
        _log_file.write(line)
        _log_file.flush()
    elif not stderr:
        sys.stdout.write(line)
    else:
        sys.stderr.write(line)


def error(message: str):
    """Shorthand for log(..., ERROR).
    :param message Error message to log.
    """
    log(message, ERROR)


def info(message: str):
    """Shorthand for log(..., INFO)
    :param message Informational message to log.
    """
    log(message, INFO)


def log(message: str, severity: int=DEBUG):
    """Outputs the given message with the given severity.

    :param message String to output to the log
    :param severity Message severity. Optional, default is DEBUG. Severities DEBUG and INFO cause output to stdout;
        severities WARNING and ERROR print the message to stderr.
    """
    global _log_file
    # Ignore everything with the severity lower than we're interested in
    if severity < minimum_severity:
        return

    # Translate severity into text
    if severity == ERROR:
        label = 'ERROR: '
    elif severity == WARNING:
        label = 'Warning: '
    elif severity == INFO:
        label = '[i] '
    else:
        label = ''

    # Add a timestamp
    message = datetime.datetime.now().strftime('%H:%M:%S.%f') + '  ' + label + message

    # Output the message
    _write_line(message, severity > INFO)


def separator():
    """Output a separator line."""
    _write_line('=' * output_width, False)


def set_log_file(file_name: [str, None]):
    """Use the specified file as a log file.
    :param file_name Name of the log file. If None, no log file is used, and all output goes to stdout/stderr.
    """
    global _log_file
    # Close the current file, if any
    if _log_file is not None:
        _log_file.close()
        _log_file = None

    # Open the specified file for writing, if necessary
    if file_name is not None:
        _log_file = open(file_name, 'w')


def warning(message: str):
    """Shorthand for log(..., WARNING)
    :param message Warning message to log.
    """
    log(message, WARNING)


# Register a shutdown procedure
atexit.register(_teardown)
