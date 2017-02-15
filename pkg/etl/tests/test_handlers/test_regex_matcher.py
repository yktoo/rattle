from etl import config
from etl.handlers import regex_matcher


# The default configuration
_config = {
    'input_param':  'in',
    'output_param': 'out',
    'regex':        r'(\d{2,3})',  # Find 2- or 3-digit occurrences
    'group_num':    1,
    'in':           'kjrxfhw457t2c45bf82c5g2345tg83254tc28054t82g54t0x2875gt\nwqckj5t2i528542854t92cggtygc2jhgfcx28'
}


def test_defaults():
    """handlers.regex_matcher: test default invocation"""
    result = regex_matcher.Handler().run(config.Config(_config))
    print(result)
    assert result['out'] == \
        '457\n' \
        '45\n'  \
        '82\n'  \
        '234\n' \
        '832\n' \
        '54\n'  \
        '280\n' \
        '54\n'  \
        '82\n'  \
        '54\n'  \
        '287\n' \
        '528\n' \
        '542\n' \
        '854\n' \
        '92\n'  \
        '28\n'


def test_unique():
    """handlers.regex_matcher: test unique"""
    result = regex_matcher.Handler().run(config.Config(_config, unique=True))
    # We can't rely on order in this

    print(result)
    assert result['out'] == \
        '457\n' \
        '45\n'  \
        '82\n'  \
        '234\n' \
        '832\n' \
        '54\n'  \
        '280\n' \
        '287\n' \
        '528\n' \
        '542\n' \
        '854\n' \
        '92\n'  \
        '28\n'

