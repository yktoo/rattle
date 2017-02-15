from etl import config
from etl.handlers import line_merger


# The default configuration
_config = {
    'input_param':        'in',
    'output_param':       'out',
    'num_lines_to_merge': 2,
    'in':
        'line_1\n'
        'line_2\n'
        '  line_3\n'
        'line_4\n'
        '\n'
        'line_6  \n'
        'line_7'
}


def test_defaults():
    """handlers.line_merger: test default invocation"""
    result = line_merger.Handler().run(config.Config(_config))
    print(result)
    assert result['out'] == \
        'line_1line_2\n'    \
        '  line_3line_4\n'  \
        'line_6  \n'        \
        'line_7\n'


def test_start_line():
    """handlers.line_merger: test start_line"""
    result = line_merger.Handler().run(config.Config(_config, start_line=2))
    print(result)
    assert result['out'] == \
        'line_2  line_3\n'  \
        'line_4\n'          \
        'line_6  line_7\n'


def test_trim_lines():
    """handlers.line_merger: test trim_lines"""
    result = line_merger.Handler().run(config.Config(_config, trim_lines=True))
    print(result)
    assert result['out'] == \
        'line_1line_2\n'    \
        'line_3line_4\n'    \
        'line_6\n'          \
        'line_7\n'


def test_skip_blank_lines():
    """handlers.line_merger: test skip_blank_lines"""
    result = line_merger.Handler().run(config.Config(_config, skip_blank_lines=True))
    print(result)
    assert result['out'] == \
        'line_1line_2\n'    \
        '  line_3line_4\n'  \
        'line_6  line_7\n'


def test_delimiter():
    """handlers.line_merger: test delimiter"""
    result = line_merger.Handler().run(config.Config(_config, delimiter=':)'))
    print(result)
    assert result['out'] == \
        'line_1:)line_2\n'    \
        '  line_3:)line_4\n'  \
        ':)line_6  \n'        \
        'line_7\n'
