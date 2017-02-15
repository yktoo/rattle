from unittest.mock import patch, MagicMock, DEFAULT
from nose.tools import raises
from urllib.request import OpenerDirector, HTTPSHandler
from urllib.error import URLError, HTTPError
from ssl import CERT_NONE
from etl import utils
from etl import errors


_http_content = b'SomeMockedData'
_http_url = 'http://fake.url.com'
_handlers = []


def _store_handlers(*handlers):
    """Stores the provided handlers globally"""
    global _handlers
    _handlers = handlers
    return DEFAULT


def _emulate_invalid_cert(url):
    """Raise an URLError if handlers doesn't contain a corresponding handler, as if an invalid certificate was presented
    by the server
    """
    for handler in _handlers:
        # Acessing handler's context via a protected field is a bit wacky...
        if isinstance(handler, HTTPSHandler) and handler._context.verify_mode == CERT_NONE:
            return DEFAULT
    raise URLError('Something fishy is going on here!')


@patch('etl.utils.request.build_opener')
def _invoke_fetch(existing, valid_cert, fail_on_404, verify_cert, username, pwd, mock_build):
    """Invoke the function under test with the given arguments and return the fetch result"""
    # Create a mocked OpenerDirector implementation
    mock_opener = MagicMock(spec=OpenerDirector)
    mock_build.return_value = mock_opener
    mock_build.side_effect = _store_handlers

    # Make the opener return a mocked response, whose read() method returns the expected content
    mock_response = MagicMock()
    mock_response.read.return_value = _http_content
    mock_opener.open.return_value = mock_response

    # If we're to emulate a 404 error, make the open() fail
    if not existing:
        mock_opener.open.side_effect = HTTPError(_http_url, 404, 'Ai-ai-ai', None, None)

    # If we're to emulate an invalid certificate
    elif not valid_cert:
        mock_opener.open.side_effect = _emulate_invalid_cert

    # Call the fetch
    result = utils.http_fetch(_http_url, fail_on_404, verify_cert, username, pwd)

    # Verify open() and read() were (not) called
    mock_opener.open.assert_called_once_with(_http_url)
    if existing:
        mock_response.read.assert_called_once_with()
    else:
        assert mock_response.read.call_count == 0

    return result


def test_http_fetch_existing():
    """utils: http_fetch: test fetching existing URL"""
    result = _invoke_fetch(True, True, True, True, None, '')
    assert result == _http_content


def test_http_fetch_nonexistent_ok():
    """utils: http_fetch: test fetching nonexistent optional URL"""
    result = _invoke_fetch(False, True, False, True, None, '')
    assert result is None


@raises(errors.HttpError)
def test_http_fetch_nonexistent_fail():
    """utils: http_fetch: test fetching nonexistent mandatory URL"""
    _invoke_fetch(False, True, True, True, None, '')


def test_http_fetch_invalid_ssl_cert_ok():
    """utils: http_fetch: test fetching HTTPS page with invalid certificate without enforcing"""
    result = _invoke_fetch(True, False, True, False, None, '')
    assert result == _http_content


@raises(URLError)
def test_http_fetch_invalid_ssl_cert_fail():
    """utils: http_fetch: test fetching HTTPS page with invalid certificate with enforcing"""
    _invoke_fetch(True, False, True, True, None, '')
