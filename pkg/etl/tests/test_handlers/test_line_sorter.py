from etl import config
from etl.handlers import line_sorter


# The default configuration
_config = {
    'input_param':  'in',
    'output_param': 'out',
    'in':
        'zyx\n'
        'xyz\n'
        'abc\n'
        '\n'
        'def\n'
        '%$#'
}


def test_defaults():
    """handlers.line_sorter: test default sort"""
    result = line_sorter.Handler().run(config.Config(_config))
    print(result)
    assert result['out'] == \
        '\n'                \
        '%$#\n'             \
        'abc\n'             \
        'def\n'             \
        'xyz\n'             \
        'zyx\n'


def test_reverse():
    """handlers.line_sorter: test reverse sort"""
    result = line_sorter.Handler().run(config.Config(_config, reverse=True))
    print(result)
    assert result['out'] == \
        'zyx\n'             \
        'xyz\n'             \
        'def\n'             \
        'abc\n'             \
        '%$#\n'             \
        '\n'
