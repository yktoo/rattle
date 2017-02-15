from unittest.mock import patch
from unittest.mock import MagicMock
from etl import config
from etl.handlers import sql_query


@patch('etl.handlers.sql_query.context')
def _invoke_with(sql, conf, mock_context):
    """Run the handler with the specified config, in a mocked context. Return a tuple consisting of the handler's result
    and the mocked DB cursor object."""
    # Create a fake DB connection and a cursor
    mock_db = MagicMock()
    mock_db.cursor.return_value = mock_cursor = MagicMock()

    # Mock iterator result and column headers of the cursor
    mock_cursor.__iter__.return_value = [['abc', 'def', 10, True], ['ghi', 'jkl', 42, False]]
    mock_cursor.description = [['str1'], ['str2'], ['int'], ['bool']]

    # Set up our fake context
    mock_context.get_db_connection.return_value = mock_db

    # Run the handler
    result = sql_query.Handler().run(config.Config({'database': 'mockdb', 'sql': sql}, **conf))

    # Verify our DB was requested
    mock_context.get_db_connection.assert_called_once_with('mockdb')

    # Check the cursor was requested and closed after use
    mock_db.cursor.assert_called_once_with()
    mock_cursor.close.assert_called_once_with()
    return result, mock_cursor


def test_default():
    """handlers.sql_query: test query with defaults"""
    result, cur = _invoke_with('TEST_QUERY_1', {})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_1', {})
    # Check query result
    assert result['data'] == 'abcdef10True\nghijkl42False\n'


def test_output_param():
    """handlers.sql_query: test output param mapping"""
    result, cur = _invoke_with('TEST_QUERY_2', {'output_param': 'xYz'})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_2', {})
    # Check query result
    assert result['xYz'] == 'abcdef10True\nghijkl42False\n'


def test_delimiters():
    """handlers.sql_query: test field and record delimiters"""
    result, cur = _invoke_with('TEST_QUERY_3', {'field_delimiter': '|', 'record_delimiter': 'FOO'})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_3', {})
    # Check query result
    assert result['data'] == 'abc|def|10|TrueFOOghi|jkl|42|FalseFOO'


def test_col_headers():
    """handlers.sql_query: test column headers"""
    result, cur = _invoke_with('TEST_QUERY_4', {'col_headers': True, 'field_delimiter': '*'})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_4', {})
    # Check query result
    assert result['data'] == 'str1*str2*int*bool\nabc*def*10*True\nghi*jkl*42*False\n'


def test_quotechar_bracket():
    """handlers.sql_query: test quote char of '('"""
    result, cur = _invoke_with('TEST_QUERY_5', {'quotechar': '('})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_5', {})
    # Check query result
    assert result['data'] == '(abc)(def)(10)(True)\n(ghi)(jkl)(42)(False)\n'


def test_quotechar_sq_bracket():
    """handlers.sql_query: test quote char of '['"""
    result, cur = _invoke_with('TEST_QUERY_6', {'quotechar': '['})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_6', {})
    # Check query result
    assert result['data'] == '[abc][def][10][True]\n[ghi][jkl][42][False]\n'


def test_quotechar_brace():
    """handlers.sql_query: test quote char of '{'"""
    result, cur = _invoke_with('TEST_QUERY_7', {'quotechar': '{'})
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_7', {})
    # Check query result
    assert result['data'] == '{abc}{def}{10}{True}\n{ghi}{jkl}{42}{False}\n'


def test_params():
    """handlers.sql_query: test parameter binding and substitution"""
    result, cur = _invoke_with(
        'TEST_QUERY_8',
        {
            'params': [
                {'name': 'X', 'value': '123'},
                {'name': 'Y', 'value': '{SUBST}'}
            ],
            'SUBST': '_text_'
        }
    )
    # Check query was executed
    cur.execute.assert_called_once_with('TEST_QUERY_8', {'X': '123', 'Y': '_text_'})
