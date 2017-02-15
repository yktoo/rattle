from nose.tools import raises
from etl.handlers import base


@raises(TypeError)
def test_class_is_abstract():
    """handlers.base: verify that the base handler class is abstract"""
    base.Handler()
