from nose.tools import raises
from etl import config
from etl import errors

_conf = None  # Our local configuration object to test


def setup_module():
    global _conf
    _conf = config.Config({
        'key_str':  'value_str',
        'key_int':  42,
        'key_bool': True,
        'key_list': [1, 2, 3, 4],
        'key_text': 'several lines\nas textual\nvalue',
        'key_dict': {
            'nested_int_key': 1,
            'nested_dict_key': {
                'nested2_key': 1
            }
        }
    })


def test_existing_key_str_val():
    """config: test reading string values for an existing key"""
    global _conf
    assert _conf['key_str'] == 'value_str'


def test_existing_key_int_val():
    """config: test reading integer values for an existing key"""
    global _conf
    assert _conf['key_int'] == 42


def test_existing_key_bool_val():
    """config: test reading boolean values for an existing key"""
    global _conf
    assert _conf['key_bool']


def test_existing_key_list_val():
    """config: test reading list values for an existing key"""
    global _conf
    assert _conf['key_list'] == [1, 2, 3, 4]


def test_existing_key_with_default():
    """config: test reading a value for an existing key if default is given"""
    global _conf
    assert _conf['key_int', 14] == 42


def test_dict_conversion():
    """config: test converting incoming dict values into Config instances"""
    global _conf
    assert type(_conf['key_dict']) is config.Config
    assert type(_conf['key_dict']['nested_dict_key']) is config.Config


def test_existing_key_lines_iter():
    """config: test reading text value via line iterator"""
    global _conf
    # Check line count
    i = 0
    for line in _conf.lines('key_text'):
        i += 1
        # All but the list line should end with a linebreak
        if i < 3:
            assert line.endswith('\n')
    assert i == 3


def test_existing_key_lines_list():
    """config: test reading text value via line list"""
    global _conf
    llist = _conf.lines_list('key_text')
    assert len(llist) == 3
    assert llist[0] == 'several lines'
    assert llist[1] == 'as textual'
    assert llist[2] == 'value'


def test_nonexistent_key_with_default():
    """config: test reading a value for a nonexistent key if default is given"""
    global _conf
    assert _conf['fake', 100] == 100


@raises(errors.ConfigError)
def test_nonexistent_key_without_default():
    """config: test reading a value for a nonexistent key if no default is given"""
    global _conf
    return _conf['fake']


def test_setting_str_value():
    """config: test setting string value"""
    c = config.Config()
    c['a'] = 'string'
    assert c['a'] == 'string'


def test_setting_int_value():
    """config: test setting integer value"""
    c = config.Config()
    c['a'] = 1
    assert c['a'] == 1


def test_setting_bool_value():
    """config: test setting boolean value"""
    c = config.Config()
    c['a'] = True
    assert c['a']


def test_setting_list_value():
    """config: test setting list value"""
    c = config.Config()
    c['a'] = [5, 6, 'x']
    assert type(c['a']) is list
    assert c['a'] == [5, 6, 'x']


def test_setting_dict_value():
    """config: test setting dict value and autoconversion to Config"""
    c = config.Config()
    c['a'] = {'k': 'v'}
    assert type(c['a']) is config.Config
    assert c['a']['k'] == 'v'


def test_update():
    """config: test update"""
    c = config.Config({'a': 1, 'b': 'xxx', 'c': False})
    c.update({'b': 400, 'c': 17}, d='new', e={'nested': 5})
    assert c['a'] == 1
    assert c['b'] == 400
    assert c['c'] == 17
    assert c['d'] == 'new'
    assert type(c['e']) is config.Config
    assert c['e']['nested'] == 5

