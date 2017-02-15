"""
Helper classes/functions for testing.
"""

from copy import deepcopy
from unittest.mock import MagicMock


class CopyingMock(MagicMock):
    """A special flavour of MagicMock that copies function arguments by value rather than by reference. This
    implementation is taken from
    https://docs.python.org/3/library/unittest.mock-examples.html#coping-with-mutable-arguments
    """
    def __call__(self, *args, **kwargs):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        return super(CopyingMock, self).__call__(*args, **kwargs)
