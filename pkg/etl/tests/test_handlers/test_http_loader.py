from unittest.mock import patch
from etl import config
from etl.handlers import http_loader
from etl.tests import helpers


# Content returned by mocked http_fetch
_http_base_url    = 'http://fake_url/'
_http_content_str = '**CONTENT**'
_http_content_bin = _http_content_str.encode()
_http_content_gz  = b'\x1F\x8B_some_data_'


def _invoke_simple(conf: dict, out_param: str, fetched_data: bytes, expected_data: str):
    """Invoke the handler in 'simple' mode and check the result."""
    with patch('etl.handlers.http_loader.utils.http_fetch', return_value=fetched_data) as mocked_fetch:
        # Instantiate and run the handler
        h = http_loader.Handler()
        result = h.run(config.Config(conf))

        # Check the result
        assert result[out_param] == expected_data
        mocked_fetch.assert_called_once_with(_http_base_url, True, True, None, '')


# NB: We're patching with CopyingMock here as we need to check child handler invocations by value rather than by
# reference, as MagicMock does (coz dicts that are arguments to invoke_handler() are mutable).
# See https://docs.python.org/3/library/unittest.mock-examples.html#coping-with-mutable-arguments for details.
@patch('etl.handlers.http_loader.context.invoke_handler', new_callable=helpers.CopyingMock)
@patch('etl.handlers.http_loader.utils.http_fetch', return_value=_http_content_bin)
def _invoke_filedefs(conf, mocked_fetch, mocked_invoke):
    """Invoke the handler for file defs, and return two mocks."""
    # Instantiate and run the handler
    h = http_loader.Handler()
    h.run(config.Config(conf))
    return mocked_fetch, mocked_invoke


@patch('etl.handlers.http_loader.context.invoke_handler', new_callable=helpers.CopyingMock)
@patch('etl.handlers.http_loader.utils.http_fetch', return_value=None)
def _invoke_nonexistent(conf, mocked_fetch, mocked_invoke):
    """Invoke the handler with http_fetch() that pretends to not find the file."""
    # Instantiate and run the handler
    h = http_loader.Handler()
    h.run(config.Config(conf))
    return mocked_fetch, mocked_invoke


def test_simple_default():
    """handlers.http_loader: test simple invocation with defaults"""
    _invoke_simple({'base_url': _http_base_url}, 'data', _http_content_bin, _http_content_str)


def test_simple_url_subst():
    """handlers.http_loader: test simple invocation with base URL param substitution"""
    _invoke_simple({'MY_URL': _http_base_url, 'base_url': '{MY_URL}'}, 'data', _http_content_bin, _http_content_str)


def test_simple_output_param():
    """handlers.http_loader: test simple invocation with output param mapping"""
    _invoke_simple({'base_url': _http_base_url, 'output_param': 'OUT'}, 'OUT', _http_content_bin, _http_content_str)


def test_simple_compr_detection_raw():
    """handlers.http_loader: test simple invocation with compressed file detection and raw input"""
    _invoke_simple(
        {'base_url': _http_base_url, 'detect_compressed': True},
        'data',
        _http_content_bin,
        _http_content_str
    )


def test_simple_compr_detection_gzipped():
    """handlers.http_loader: test simple invocation with compressed file detection and gzipped input"""
    with patch('etl.handlers.http_loader.GzipFile.read', return_value=_http_content_bin) as mocked_gz_read:
        _invoke_simple(
            {'base_url': _http_base_url, 'detect_compressed': True},
            'data',
            _http_content_gz,
            _http_content_str
        )
        # Make sure the fake gzip-read method was called
        assert mocked_gz_read.call_count == 1


def test_simple_ignore_invalid_cert():
    """handlers.http_loader: test simple invocation with ignoring invalid SSL certificate"""
    with patch('etl.handlers.http_loader.utils.http_fetch') as mocked_fetch:
        # Instantiate and run the handler
        h = http_loader.Handler()
        h.run(config.Config({'base_url': _http_base_url, 'verify_cert': False}))

        # Check the result
        mocked_fetch.assert_called_once_with(_http_base_url, True, False, None, '')


def test_simple_auth():
    """handlers.http_loader: test simple invocation with authentication"""
    with patch('etl.handlers.http_loader.utils.http_fetch') as mocked_fetch:
        # Instantiate and run the handler
        h = http_loader.Handler()
        h.run(config.Config({'base_url': _http_base_url, 'username': 'JOHN', 'password': 'DOE'}))

        # Check the result
        mocked_fetch.assert_called_once_with(_http_base_url, True, True, 'JOHN', 'DOE')


def test_filedefs_default():
    """handlers.http_loader: test file defs with defaults"""
    mocks = _invoke_filedefs({
        'base_url': _http_base_url,
        'file_defs': [
            config.Config({
                'name': 'file_A',
                'handler': {}
            })
        ]
    })
    # Check http_fetch() invocation
    mocks[0].assert_called_once_with(_http_base_url + 'file_A', True, True, None, '')
    # Check handler invocation
    mocks[1].assert_called_once_with({}, {'file_name': 'file_A', 'data': _http_content_str})


def test_filedefs_url_subst():
    """handlers.http_loader: test file defs with URL param substitution"""
    mocks = _invoke_filedefs({
        'MY_BASE': _http_base_url,
        'MY_FILE': 'file_',
        'base_url': '{MY_BASE}',
        'file_defs': [
            config.Config({
                'name': '{MY_FILE}x',
                'handler': {}
            })
        ]
    })
    # Check http_fetch() invocation
    mocks[0].assert_called_once_with(_http_base_url + 'file_x', True, True, None, '')
    # Check handler invocation
    mocks[1].assert_called_once_with({}, {'file_name': 'file_x', 'data': _http_content_str})


def test_filedefs_out_param():
    """handlers.http_loader: test file defs with output param mapping"""
    mocks = _invoke_filedefs({
        'base_url': _http_base_url,
        'output_param': 'TEST',
        'file_defs': [
            config.Config({
                'name': 'file_B',
                'handler': {}
            })
        ]
    })
    # Check handler invocation
    mocks[1].assert_called_once_with({}, {'file_name': 'file_B', 'TEST': _http_content_str})


def test_filedefs_passthrough():
    """handlers.http_loader: test file defs with passing-through params"""
    mocks = _invoke_filedefs({
        'base_url': _http_base_url,
        'a': 42,
        'b': 'yes',
        'passthrough_params': ['a', 'b'],
        'file_defs': [
            config.Config({
                'name': 'file_C',
                'handler': {}
            })
        ]
    })
    # Check handler invocation
    mocks[1].assert_called_once_with({}, {'file_name': 'file_C', 'data': _http_content_str, 'a': 42, 'b': 'yes'})


def test_filedefs_compr_detection_raw():
    """handlers.http_loader: test file defs with compressed file detection and raw input"""
    mocks = _invoke_filedefs({
        'base_url': _http_base_url,
        'detect_compressed': True,
        'file_defs': [
            config.Config({
                'name': 'file_D',
                'handler': {}
            })
        ]
    })
    # Check http_fetch() invocation
    mocks[0].assert_called_once_with(_http_base_url + 'file_D', True, True, None, '')
    # Check handler invocation
    mocks[1].assert_called_once_with({}, {'file_name': 'file_D', 'data': _http_content_str})


def test_filedefs_nonexistent_ok():
    """handlers.http_loader: test file defs with non-mandatory nonexisting URL"""
    mocks = _invoke_nonexistent({
        'base_url': _http_base_url,
        'file_defs': [
            config.Config({
                'name': 'fake',
                'required': False,
                'handler': {}
            })
        ]
    })
    # Check http_fetch() invocation
    mocks[0].assert_called_once_with(_http_base_url + 'fake', False, True, None, '')
    # Check handler invocation never happened
    assert not mocks[1].called
