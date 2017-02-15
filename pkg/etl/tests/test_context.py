from os import sep, path
from contextlib import contextmanager
from nose.tools import raises
from unittest.mock import patch
from unittest.mock import call
from etl import errors
from etl import config
from etl import context


def _get_empty_handler_conf(**additional_conf):
    """Return configuration for EmptyHandler."""
    return config.Config(
        {
            'module': 'etl.tests.dummy_handlers',
            'class': 'EmptyHandler',
            'p1': 10,
            'p2': 20
        },
        **additional_conf)


@contextmanager
def configure(config_file_relpath, verbose, dry_run, global_overrides=None):
    """Handy factory function for context manager for easy testing of configurations.
    :param config_file_relpath: Configuration file path relative to this script's path.
    :param verbose: Verbosity override.
    :param dry_run: Whether to activate the dry-run mode.
    :param global_overrides: Dictionary with global parameter overrides.
    """
    context.initialise(
        path.join(path.dirname(__file__), config_file_relpath),
        verbose,
        dry_run,
        global_overrides if global_overrides is not None else {})
    try:
        yield
    finally:
        context.teardown()


@raises(errors.LogicError)
def test_uninitialised_config_access():
    """context: test accessing config with uninitialised context"""
    context.get_config()


@raises(errors.LogicError)
def test_uninitialised_db_connection_access():
    """context: test accessing DB connections with uninitialised context"""
    context.get_db_connection('dummy')


def test_empty_config():
    """context: test empty config"""
    with configure('empty.json', None, False):
        assert len(context.get_config()) == 0
        # Validate dry-run settings
        assert not context.dry_run_mode
        assert context.dry_run_prefix == ''


def test_verbosity():
    """context: test verbosity settings"""
    # Test defaults
    with configure('empty.json', None, False):
        assert not context.verbose_mode

    # Test default overrides
    with configure('empty.json', False, False):
        assert not context.verbose_mode
    with configure('empty.json', True, False):
        assert context.verbose_mode

    # Test config spec
    with configure('log_verbose_true.json', None, False):
        assert context.verbose_mode

    # Test config spec overrides
    with configure('log_verbose_true.json', False, False):
        assert not context.verbose_mode
    with configure('log_verbose_false.json', True, False):
        assert context.verbose_mode


def test_dry_run():
    """context: test dry-run settings"""
    with configure('empty.json', None, True):
        assert context.dry_run_mode
        assert context.dry_run_prefix != ''


@patch('etl.context.DBConnection')
def test_db_connection(mock_db):
    """context: test establishing DB connection"""
    with configure('db_conn_a.json', None, False):
        context.get_db_connection("db")

        # The DB connection must be created exactly one time
        mock_db.assert_called_once_with('a', 'b', 'c')

        # Repeated requests to the same DB should not recreate the connection
        context.get_db_connection("db")
        assert mock_db.call_count == 1


@raises(errors.ConfigError)
def test_db_connection_incomplete():
    """context: test DB connection with incomplete spec"""
    with configure('db_conn_incomplete.json', None, False):
        context.get_db_connection("dbIncomplete")


@patch('etl.context.DBConnection')
def test_db_connection_passwd_base64(mock_db):
    """context: test DB connection with Base64-encoded password"""
    with configure('db_conn_base64.json', None, False):
        context.get_db_connection("dbBase64")

        # Verify the password is correctly Base64-decoded
        mock_db.assert_called_once_with('Secret', 'Facility', 'TopSecret')


@patch('etl.context.DBConnection')
def test_db_conn_external_ok(mock_db):
    """context: test DB connection defined in an external file"""
    with configure('db_conn_ext.json', None, False):
        context.get_db_connection("dbExt")

        # The DB connection's parameters must be read from the external file, then it must be created
        mock_db.assert_called_once_with('TheConnection', 'Mickey', 'Mouse')

        # Repeated requests to the same DB should not recreate the connection
        context.get_db_connection("dbExt")
        assert mock_db.call_count == 1


@patch('etl.context.DBConnection')
def test_db_conn_external_wglob(mock_db):
    """context: test external DB connection defined via a global"""
    with configure('db_conn_ext_glob.json', None, False, {'PATH_FROM_GLOBAL': 'db_conn_extdef.json'}):
        context.get_db_connection("dbExtGlob")
        mock_db.assert_called_once_with('TheConnection', 'Mickey', 'Mouse')


@raises(FileNotFoundError)
def test_db_conn_external_nonexistent():
    """context: test DB connection referring to a nonexistent file"""
    with configure('db_conn_ext_err.json', None, False):
        context.get_db_connection("dbExtErr")


@raises(errors.ConfigError)
def test_db_connection_undefined():
    """context: test fetching undefined DB connection"""
    with configure('db_empty.json', None, False):
        context.get_db_connection("fake")


@raises(errors.ConfigError)
def test_invoke_misconfiguration():
    """context: test invoking handler with config of a wrong type"""
    context.invoke_handler(42)


@patch('etl.tests.dummy_handlers.EmptyHandler.run', return_value={})
def test_invoke_single_handler(handler_run):
    """context: test single handler invocation"""
    context.invoke_handler(_get_empty_handler_conf(), {'p1': 11, 'p3': 30})

    # Verify handler has run
    handler_run.assert_called_once_with({
        'module': 'etl.tests.dummy_handlers',
        'class':  'EmptyHandler',
        'p1':     10,   # Local handler config must override parent config
        'p2':     20,   # Local config must be passed to handler
        'p3':     30    # Parent config must be passed to handler
    })


# Our mocked handler will be multiplying p2 value by 5
@patch('etl.tests.dummy_handlers.EmptyHandler.run', side_effect=lambda conf: {'p2': conf['p2'] * 5})
def test_invoke_chained_handlers(handler_run):
    """context: test chained handlers invocation"""
    # Run a chain of two EmptyHandlers
    context.invoke_handler([_get_empty_handler_conf(), _get_empty_handler_conf()])

    # Verify handler runs
    print(handler_run.call_args_list)
    assert handler_run.call_count == 2
    assert \
        handler_run.call_args_list == [
            call({'p1': 10, 'p2': 20,  'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'}),
            call({'p1': 10, 'p2': 100, 'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'})
        ], \
        'p2 gets multiplied by 5'


# Our mocked handler will be incrementing p3
@patch('etl.tests.dummy_handlers.EmptyHandler.run', side_effect=lambda conf: {'p3': conf['p3'] + 1})
def test_invoke_nested_handlers(handler_run):
    """context: test nested handlers invocation"""
    # Run a number of EmptyHandlers
    context.invoke_handler([
        _get_empty_handler_conf(p3=50),
        [_get_empty_handler_conf(), _get_empty_handler_conf(), _get_empty_handler_conf()],
        _get_empty_handler_conf(),
    ])

    # Verify handler runs
    print(handler_run.call_args_list)
    assert handler_run.call_count == 5
    assert \
        handler_run.call_args_list == [
            call({'p1': 10, 'p2': 20, 'p3': 50, 'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'}),
            # Here we're going into a sub-pipeline
            call({'p1': 10, 'p2': 20, 'p3': 51, 'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'}),
            call({'p1': 10, 'p2': 20, 'p3': 52, 'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'}),
            call({'p1': 10, 'p2': 20, 'p3': 53, 'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'}),
            # Here we come back out again
            call({'p1': 10, 'p2': 20, 'p3': 54, 'module': 'etl.tests.dummy_handlers', 'class': 'EmptyHandler'}),
        ]


@patch('etl.tests.dummy_handlers.EmptyHandler.run')
def test_param_block(handler_run):
    """context: test publishing parameter blocks on pipeline"""
    # Run a chain of two EmptyHandlers
    context.invoke_handler([
        config.Config({'a': 42, 'b': 43}),
        _get_empty_handler_conf()
    ])

    # Verify handler has run
    handler_run.assert_called_once_with({
        'module': 'etl.tests.dummy_handlers',
        'class':  'EmptyHandler',
        'p1':     10,
        'p2':     20,
        'a':      42,
        'b':      43,
    })


def test_get_absolute_filename_abs():
    """context: test getting absolute file name with absolute path as input"""
    fname = sep + 'some' + sep + 'path'
    with configure('empty.json', None, False):
        assert context.get_absolute_file_name(fname) == fname


def test_get_absolute_filename_rel():
    """context: test getting absolute file name with relative path as input"""
    with configure('empty.json', None, False):
        assert \
            context.get_absolute_file_name('some' + sep + 'path') == path.join(path.dirname(__file__), 'some', 'path')


@patch('etl.tests.dummy_handlers.EmptyHandler.run')
def test_invoke_and_include_relative(handler_run):
    """context: test config file inclusion by relative path"""
    with configure('empty.json', None, False):
        context.invoke_handler('test_conf.include.json')

        # Verify handler runs
        print(handler_run.call_args_list)
        handler_run.assert_called_once_with({
            'module': 'etl.tests.dummy_handlers',
            'class': 'EmptyHandler',
            'p1': 100
        })


@patch('etl.tests.dummy_handlers.EmptyHandler.run')
def test_invoke_and_include_absolute(handler_run):
    """context: test config file inclusion by absolute path"""
    with configure('empty.json', None, False):
        context.invoke_handler(path.join(path.dirname(__file__), 'test_conf_2.include.json'))

        # Verify handler runs
        print(handler_run.call_args_list)
        handler_run.assert_called_once_with({
            'module': 'etl.tests.dummy_handlers',
            'class': 'EmptyHandler',
            'p1': 200
        })


@patch('etl.tests.dummy_handlers.EmptyHandler.run')
def test_globals(handler_run):
    """context: test globals specification in config file"""
    with configure('globals.json', None, False, {}):
        # Run a handler
        context.invoke_handler(_get_empty_handler_conf())

        # Verify the handler has run
        handler_run.assert_called_once_with({
            'module': 'etl.tests.dummy_handlers',
            'class':  'EmptyHandler',
            'p1':     10,
            'p2':     20,
            # Must have been called with these globals
            'param_a': 'A',
            'param_b': 14
        })


@patch('etl.tests.dummy_handlers.EmptyHandler.run')
def test_global_overrides(handler_run):
    """context: test globals specification overrides"""
    with configure('globals.json', None, False, {'param_b': 'TEST', 'param_c': 700}):
        # Run a handler
        context.invoke_handler(_get_empty_handler_conf())

        # Verify the handler has run
        handler_run.assert_called_once_with({
            'module': 'etl.tests.dummy_handlers',
            'class':  'EmptyHandler',
            'p1':     10,
            'p2':     20,
            'param_a': 'A',     # Unchanged global param
            'param_b': 'TEST',  # Overridden global param
            'param_c': 700      # New global param
        })
