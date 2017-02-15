from io import StringIO
from unittest.mock import patch
from unittest.mock import MagicMock
from nose.tools import raises
from etl import config
from etl import loader


_config_file = StringIO()


def _get_loader_instance() -> loader.Loader:
    """Instantiates and returns a new Loader."""
    return loader.Loader(_config_file, None, False, {})


def _get_mock_process_config(name, handler, stop_on_error) -> config.Config:
    """Create and return mock process configuration."""
    return MagicMock(
        return_value=config.Config({
            'processes': [
                config.Config({
                    'name':          name,
                    'handler':       handler,
                    'stop_on_error': stop_on_error
                })
            ]
        }))


@patch('etl.loader.context')
def test_loader_initialisation(mock_context):
    """loader: test Loader initialisation"""
    # Instantiate a loader
    _get_loader_instance()
    mock_context.initialise.assert_called_once_with(_config_file, None, False, {})


@patch('etl.loader.context')
def test_loader_run(mock_context):
    """loader: test running Loader"""
    # Describe a dummy process
    mock_context.get_config = _get_mock_process_config('test', 'dummy', True)

    # Instantiate and run the loader
    ldr = _get_loader_instance()
    succeeded = ldr.run()
    assert succeeded
    mock_context.invoke_handler.assert_called_once_with('dummy')


@patch('etl.loader.logger')
@patch('etl.loader.context')
def test_loader_error_ignore(mock_context, mock_logger):
    """loader: test that Loader can ignore process errors"""
    # Describe a dummy process
    mock_context.get_config = _get_mock_process_config('test', 'dummy', False)

    # Make handler invocation fail
    mock_context.invoke_handler = MagicMock(side_effect=Exception('Boom!'))

    # Instantiate and run the loader
    ldr = _get_loader_instance()
    succeeded = ldr.run()
    assert not succeeded
    mock_context.invoke_handler.assert_called_once_with('dummy')
    assert mock_logger.error.call_count == 1  # The exception must be logged as an error


@raises(SystemExit)
@patch('etl.loader.logger')
@patch('etl.loader.context')
def test_loader_error_stop(mock_context, mock_logger):
    """loader: test that Loader can exit on process errors"""
    # Describe a dummy process
    mock_context.get_config = _get_mock_process_config('test', 'dummy', True)

    # Make handler invocation fail
    mock_context.invoke_handler = MagicMock(side_effect=Exception('Boom!'))

    # Instantiate and run the loader
    ldr = _get_loader_instance()
    ldr.run()
