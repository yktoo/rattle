from unittest.mock import patch
from unittest.mock import call
from etl import config
from etl.handlers import line_iterator
from etl.tests import helpers


# The default configuration
_config = {
    'input_param':  'few_lines',
    'output_param': 'one_line',
    'few_lines':
        'line_1\n'
        'line_2\n'
        '\n'
        'line_4',
    'handler':      {}
}


# NB: We're patching with CopyingMock here as we need to check child handler invocations by value rather than by
# reference, as MagicMock does (coz dicts that are arguments to invoke_handler() are mutable).
# See https://docs.python.org/3/library/unittest.mock-examples.html#coping-with-mutable-arguments for details.
@patch('etl.handlers.line_iterator.context.invoke_handler', new_callable=helpers.CopyingMock)
def _invoke_with(extra_conf, mocked_invoke):
    """Invoke the handler with patched context.invoke_handler(), and return the mock."""
    # Instantiate and run the handler
    h = line_iterator.Handler()
    h.run(config.Config(_config, **extra_conf))
    return mocked_invoke


def test_defaults():
    """handlers.line_iterator: test default invocation"""
    # Run the handler
    mk = _invoke_with({})
    # By default chomp is on and blank lines are skipped
    assert mk.call_count == 3
    print(mk.call_args_list)
    assert mk.call_args_list == [
        call({}, {'one_line': 'line_1'}),
        call({}, {'one_line': 'line_2'}),
        call({}, {'one_line': 'line_4'})
    ]


def test_blank_lines():
    """handlers.line_iterator: test blank line processing"""
    mk = _invoke_with({'skip_blank_lines': False})
    assert mk.call_count == 4
    print(mk.call_args_list)
    assert mk.call_args_list == [
        call({}, {'one_line': 'line_1'}),
        call({}, {'one_line': 'line_2'}),
        call({}, {'one_line': ''}),       # Bingo!
        call({}, {'one_line': 'line_4'})
    ]


def test_keep_linebreaks():
    """handlers.line_iterator: test keeping linebreaks"""
    mk = _invoke_with({'chomp': False})
    assert mk.call_count == 4
    print(mk.call_args_list)
    assert mk.call_args_list == [
        call({}, {'one_line': 'line_1\n'}),
        call({}, {'one_line': 'line_2\n'}),
        call({}, {'one_line': '\n'}),       # This line is no longer blank
        call({}, {'one_line': 'line_4'})    # No linebreak here
    ]


def test_passthrough_params():
    """handlers.line_iterator: test passing-through parameters"""
    mk = _invoke_with({'passthrough_params': ['a', 'b', 'c'], 'a': 14, 'b': 'stuff', 'c': True})
    assert mk.call_count == 3
    print(mk.call_args_list)
    assert mk.call_args_list == [
        call({}, {'one_line': 'line_1', 'a': 14, 'b': 'stuff', 'c': True}),
        call({}, {'one_line': 'line_2', 'a': 14, 'b': 'stuff', 'c': True}),
        call({}, {'one_line': 'line_4', 'a': 14, 'b': 'stuff', 'c': True})
    ]
