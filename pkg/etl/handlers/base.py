"""
Introduces the base handler class.
"""

import abc


class Handler(object, metaclass=abc.ABCMeta):
    """The base abstract handler class."""

    @abc.abstractmethod
    def run(self, config):
        """The main worker routine of the handler. Returns a list of results, if any, otherwise None. Must be overridden
            in the derived class.
        :type config: Configuration collection specifying handler parameters.
        :rtype : dict
        """
        pass
