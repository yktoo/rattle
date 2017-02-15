"""
Declaration of a dummy handler used for unit tests.
"""
from etl.handlers import base


class EmptyHandler(base.Handler):
    def run(self, config):
        pass
