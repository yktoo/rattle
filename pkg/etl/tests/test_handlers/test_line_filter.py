from etl import config
from etl.handlers import line_filter


# The default configuration
INPUT_DATA = \
    'abc0\n' \
    'def0\n' \
    'ghi1\n' \
    '\n'     \
    'jkl1\n' \
    'xyz2\n'


def _invoke_with(extra_conf, expected_output, input_param='data', output_param='data'):
    """Invoke the handler with the specified config, and validates the result."""
    # Instantiate and run the handler
    result = line_filter.Handler().run(config.Config(
        {
            input_param: INPUT_DATA
        },
        **extra_conf))

    # Validate the result
    print(result)
    assert result[output_param] == expected_output
    return result


def test_defaults():
    """handlers.line_filter: test default invocation"""
    _invoke_with({}, INPUT_DATA)


def test_param_mapping():
    """handlers.line_filter: test parameter mapping"""
    _invoke_with({'input_param': 'IN', 'output_param': 'RESULT'}, INPUT_DATA, 'IN', 'RESULT')


def test_start_line():
    """handlers.line_filter: test skipping to start line"""
    _invoke_with(
        {'start_line': 3},
        'ghi1\n'
        '\n'
        'jkl1\n'
        'xyz2\n'
    )


def test_skip_blank_lines():
    """handlers.line_filter: test skipping blank lines"""
    _invoke_with(
        {'skip_blank_lines': True},
        'abc0\n'
        'def0\n'
        'ghi1\n'
        'jkl1\n'
        'xyz2\n'
    )


def test_single_criterion():
    """handlers.line_filter: test single criterion"""
    _invoke_with({'criteria': config.Config({'search': '1'})}, 'ghi1\njkl1\n')


def test_single_param_substitution():
    """handlers.line_filter: test single criterion with parameter substitution"""
    _invoke_with(
        {'NEEDLE': 'i1', 'criteria': config.Config({'search': '{NEEDLE}', 'substitute_params': True})},
        'ghi1\n')


def test_criteria_list():
    """handlers.line_filter: test multiple criteria"""
    _invoke_with(
        {
            'criteria': [
                config.Config({
                    'search': r'[agx]\w{2}\d$',
                    'is_regex': True
                }),
                config.Config({
                    'search': 'hi',
                    'is_regex': False
                })
            ]
        },
        'ghi1\n'
    )


def test_criteria_negation():
    """handlers.line_filter: test criteria negation"""
    _invoke_with(
        {
            'criteria': [
                config.Config({
                    'search': r'[agx]\w{2}\d$',
                    'is_regex': True,
                    'negate': False
                }),
                config.Config({
                    'search': 'hi',
                    'is_regex': False,
                    'negate': True
                })
            ]
        },
        'abc0\n'
        'xyz2\n'
    )


def test_rejected_lines():
    """handlers.line_filter: test collecting rejected lines"""
    result = _invoke_with(
        {
            'criteria': config.Config({'search': r'.*[12]$', 'is_regex': True}),
            'rejected_param': 'TRASH'
        },
        'ghi1\n'
        'jkl1\n'
        'xyz2\n'
    )

    # Check the rejected lines
    assert result['TRASH'] == 'abc0\ndef0\n\n'
