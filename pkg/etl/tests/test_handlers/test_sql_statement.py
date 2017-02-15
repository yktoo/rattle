from unittest.mock import patch
from unittest.mock import call
from unittest.mock import MagicMock
from etl import config
from etl.handlers import sql_statement


@patch('etl.handlers.sql_statement.context')
def _invoke_with(conf, dry_run, mock_context) -> MagicMock:
    """Run the handler with the specified config, in a mocked context. Return the mocked DB object."""
    # Create a fake DB connection
    mockdb = MagicMock()

    # Set up our fake context
    mock_context.dry_run_mode      = dry_run
    mock_context.dry_run_prefix    = ''
    mock_context.get_db_connection = MagicMock(return_value=mockdb)

    # Run the handler
    sql_statement.Handler().run(config.Config({'database': 'mockdb'}, **conf))

    # Verify our DB was requested
    mock_context.get_db_connection.assert_called_once_with('mockdb')
    return mockdb


def test_single_stmt_default():
    """handlers.sql_statement: test single statement with defaults"""
    db = _invoke_with({'sql': 'STATEMENT_1'}, False)
    # Check statement was executed
    db.execute.assert_called_once_with('STATEMENT_1', {})
    # Default config assumes commit after each statement
    assert db.commit.call_count == 1


def test_single_stmt_no_commit():
    """handlers.sql_statement: test single statement without implicit commit"""
    db = _invoke_with({'sql': 'STATEMENT_1', 'commit_stmt': 'none'}, False)
    # Check statement was executed
    db.execute.assert_called_once_with('STATEMENT_1', {})
    # No commit must happen
    assert not db.commit.called


def test_multiple_stmt_default():
    """handlers.sql_statement: test multiple statements with defaults"""
    db = _invoke_with({'sql': ['STATEMENT_1', 'STATEMENT_2', 'STATEMENT_3']}, False)
    # Check statements were executed
    assert db.execute.call_args_list == [
        call('STATEMENT_1', {}),
        call('STATEMENT_2', {}),
        call('STATEMENT_3', {})
    ]
    # Default config assumes commit after each statement
    assert db.commit.call_count == 3


def test_multiple_stmt_commit_all():
    """handlers.sql_statement: test multiple statements with commit set to 'all'"""
    db = _invoke_with({'sql': ['STATEMENT_1', 'STATEMENT_2', 'STATEMENT_3'], 'commit_stmt': 'all'}, False)
    # Check statements were executed
    assert db.execute.call_args_list == [
        call('STATEMENT_1', {}),
        call('STATEMENT_2', {}),
        call('STATEMENT_3', {})
    ]
    # Only one begin/commit must be issued
    assert db.begin.call_count  == 1
    assert db.commit.call_count == 1


def test_parametrised_stmt():
    """handlers.sql_statement: test parameterised statements"""
    db = _invoke_with(
        {
            'sql': ['STATEMENT_1', 'STATEMENT_2'],
            'params': [
                {'name': 'p', 'value': 'x{key1}'},
                {'name': 'q', 'value': 'y{key2}'}
            ],
            'key1': 'val_1',
            'key2': 'val_2'
        },
        False)
    # Check statements were executed
    assert db.execute.call_args_list == [
        call('STATEMENT_1', {'p': 'xval_1', 'q': 'yval_2'}),
        call('STATEMENT_2', {'p': 'xval_1', 'q': 'yval_2'})
    ]


def test_dry_run_mode():
    """handlers.sql_statement: test dry run mode"""
    db = _invoke_with({'sql': ['STATEMENT_1', 'STATEMENT_2', 'STATEMENT_3'], 'commit_stmt': 'each'}, True)
    # No executions or commits must occur
    assert not db.execute.called
    assert not db.commit.called
