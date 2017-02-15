from etl import config
from etl.handlers import str_replacer


# The default configuration
_config = {
    'input_param':  'in',
    'output_param': 'out',
    'in':           'some text\nwhich we will use\nto test our\nstring replacer'
}


def test_substring_replace():
    """handlers.str_replacer: test substring replace"""
    result = str_replacer.Handler().run(config.Config(
        _config,
        rules=[
            config.Config({'search': 'e',  'replace': '*'}),
            config.Config({'search': 't*', 'replace': 'mi'})
        ]))
    print(result)
    assert result['out'] == 'som* mixt\nwhich w* will us*\nto mist our\nstring r*plac*r'


def test_substring_replace_limit():
    """handlers.str_replacer: test substring replace limit"""
    result = str_replacer.Handler().run(config.Config(
        _config,
        rules=[
            config.Config({'search': 'e', 'replace': 'E', 'count': 3})
        ]))
    print(result)
    assert result['out'] == 'somE tExt\nwhich wE will use\nto test our\nstring replacer'


def test_regex_replace():
    """handlers.str_replacer: test regex replace"""
    result = str_replacer.Handler().run(config.Config(
        _config,
        rules=[
            # Let's swap two last letters of each word
            config.Config({'search': r'(\w)(\w)\b', 'replace': r'\2\1', 'is_regex': True})
        ]))
    print(result)
    assert result['out'] == 'soem tetx\nwhihc ew will ues\not tets oru\nstrign replacre'


def test_multi_regex_replace():
    """handlers.str_replacer: test multiple regex replace"""
    result = str_replacer.Handler().run(config.Config(
        _config,
        rules=[
            # Swap two last letters of each word
            config.Config({'search': r'(\w)(\w)\b', 'replace': r'\2\1', 'is_regex': True}),
            # Do it twice, and we're back to where we started
            config.Config({'search': r'(\w)(\w)\b', 'replace': r'\2\1', 'is_regex': True})
        ]))
    print(result)
    assert result['out'] == _config['in']


def test_regex_replace_limit():
    """handlers.str_replacer: test regex replace limit"""
    result = str_replacer.Handler().run(config.Config(
        _config,
        rules=[
            # Swap two last letters of each word for first 6 words
            config.Config({'search': r'(\w)(\w)\b', 'replace': r'\2\1', 'is_regex': True, 'count': 6})
        ]))
    print(result)
    assert result['out'] == 'soem tetx\nwhihc ew will ues\nto test our\nstring replacer'
