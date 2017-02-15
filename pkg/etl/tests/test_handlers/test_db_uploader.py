from unittest.mock import patch
from unittest.mock import call
from unittest.mock import MagicMock
from nose.tools import raises
from etl import errors
from etl import config
from etl.handlers import db_uploader


# Delimited config
_data_delimited = \
    'a,booboo,1,2.14,20141231\n' \
    'd,foofoo,4,5.6987,20150101'
_data_delimited_hdr = 'SOME IGNORED HEADER\n' + _data_delimited
_conf_delimited = {
    'data':      _data_delimited,
    'format':    'delimited',
    'delimiter': ',',
}
_mappings_delimited = [
    {'name': 'col_a', 'datatype': 'string',   'source_index': 0, 'target_column': 'A', 'length': 1},
    {'name': 'col_b', 'datatype': 'string',   'source_index': 1, 'target_column': 'B', 'length': 6},
    {'name': 'col_c', 'datatype': 'integer',  'source_index': 2, 'target_column': 'C'},
    {'name': 'col_d', 'datatype': 'number',   'source_index': 3, 'target_column': 'D'},
    {'name': 'col_e', 'datatype': 'datetime', 'source_index': 4, 'target_column': 'E'},
]

# Fixed config
_data_fixed = \
    '     a  booboo 1   2.14    20141231\n' \
    '     d  foofoo 4   5.6987  20150101'
_data_fixed_hdr = 'SOME IGNORED HEADER\n' + _data_fixed
_conf_fixed = {
    'data':   _data_fixed,
    'format': 'fixed',
}
_mappings_fixed = [
    {'name': 'col_a', 'datatype': 'string',   'source_pos':   '6:6', 'target_column': 'A', 'length': 1},
    {'name': 'col_b', 'datatype': 'string',   'source_pos':  '9:14', 'target_column': 'B', 'length': 6},
    {'name': 'col_c', 'datatype': 'integer',  'source_pos': '16:16', 'target_column': 'C'},
    {'name': 'col_d', 'datatype': 'number',   'source_pos': '20:25', 'target_column': 'D'},
    {'name': 'col_e', 'datatype': 'datetime', 'source_pos': '28:35', 'target_column': 'E'},
]

# This is what we expect to be pushed into the DB
_expected_calls = [
    call(['a', 'booboo', 1,   2.14, '20141231']),
    call(['d', 'foofoo', 4, 5.6987, '20150101']),
]


@patch('etl.handlers.db_uploader.DBArrayInserter')
@patch('etl.handlers.db_uploader.context')
def _invoke_with(base_conf, extra_conf, mappings, dry_run, mock_context, mock_inserter):
    """Run the handler with specified config."""
    # Create a fake DB connection
    mockdb = MagicMock()
    mockdb.get_param_placeholder.return_value = '.'  # Required to allow building SQL statements

    # Create a fake DBArrayInserter
    mockins = MagicMock()
    # This instance will be returned by mocked DBArrayInserter() constructor
    mock_inserter.return_value = mockins

    # Set up our fake context
    mock_context.dry_run_mode = dry_run
    mock_context.dry_run_prefix = ''
    mock_context.get_db_connection.return_value = mockdb

    # Prepare config
    conf = config.Config(
        {
            'target_database': 'mockdb',
            'target_table':    'TBL',
            'column_mappings': [config.Config(m) for m in mappings]
        },
        **base_conf)
    conf.update(**extra_conf)

    # Instantiate and run the handler
    db_uploader.Handler().run(conf)

    # Verify our DB was requested
    mock_context.get_db_connection.assert_called_with('mockdb')
    # Verify commit has [not] been done
    assert mockdb.commit.call_count == 0 if dry_run else 1
    return mockins


def test_delimited_defaults():
    """handlers.db_uploader: test loading delimited text with defaults"""
    mock_ins = _invoke_with(_conf_delimited, {}, _mappings_delimited, False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 2
    assert mock_ins.push_row.call_args_list == _expected_calls


def test_delimited_quote_char():
    """handlers.db_uploader: test loading quoted delimited text"""
    data = \
        '@a@,booboo,@1@,@2.14@,20141231\n' \
        '@d@,foofoo,@4@,@5.6987@,20150101'
    mock_ins = _invoke_with(_conf_delimited, {'quotechar': '@', 'data': data}, _mappings_delimited, False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 2
    assert mock_ins.push_row.call_args_list == _expected_calls


def test_delimited_start_line():
    """handlers.db_uploader: test loading delimited text with start_line"""
    mock_ins = _invoke_with(
        _conf_delimited,
        {'start_line': 2, 'data': _data_delimited_hdr},
        _mappings_delimited,
        False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 2
    assert mock_ins.push_row.call_args_list == _expected_calls


def test_fixed_defaults():
    """handlers.db_uploader: test loading fixed-width text with defaults"""
    mock_ins = _invoke_with(_conf_fixed, {}, _mappings_fixed, False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 2
    assert mock_ins.push_row.call_args_list == _expected_calls


def test_fixed_start_line():
    """handlers.db_uploader: test loading fixed-width text with start_line"""
    mock_ins = _invoke_with(
        _conf_fixed,
        {'start_line': 2, 'data': _data_fixed_hdr},
        _mappings_fixed,
        False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 2
    assert mock_ins.push_row.call_args_list == _expected_calls


def test_input_param():
    """handlers.db_uploader: test input param mapping"""
    mock_ins = _invoke_with(
        _conf_delimited,
        {'data': None, 'input_param': 'TABLE', 'TABLE': _data_delimited},
        _mappings_delimited,
        False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 2
    assert mock_ins.push_row.call_args_list == _expected_calls


def test_rownum():
    """handlers.db_uploader: test binding rownum expression"""
    mock_ins = _invoke_with(
        _conf_delimited,
        {'data': 'A\nB\nC'},
        [
            {'name': 'col_1', 'datatype': 'string', 'source_index': 0, 'target_column': 'COL1', 'length': 1},
            {'name': 'col_2', 'target_column': 'COL2', 'target_expr': '(SomeVar+{rownum})'},
        ],
        False)

    # Check push_row() calls
    assert mock_ins.push_row.call_count == 3
    assert mock_ins.push_row.call_args_list == [
        call(['A', 1]),
        call(['B', 2]),
        call(['C', 3]),
    ]


@raises(errors.DataError)
def test_col_overflow():
    """handlers.db_uploader: test string column overflow"""
    # The first col's value is too long so should cause an exception
    data = 'BOOM!,booboo,1,2.14,20141231'
    _invoke_with(_conf_delimited, {'data': data}, _mappings_delimited, False)


def test_dry_run():
    """handlers.db_uploader: test dry run mode"""
    mock_ins = _invoke_with(_conf_delimited, {}, _mappings_delimited, True)
    assert not mock_ins.push_row.called
