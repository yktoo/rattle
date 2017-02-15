"""
Configuration implementation.
"""
import io
from . import errors


class Config(dict):
    """Extension of the standard dict class that overrides item getter to add default value support and a better
    exception message. Based on http://stackoverflow.com/questions/2060972
    """
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, key: [str, tuple]):
        """Override the inherited getter.
        :param key Either a key name (string) or a tuple consisting of
          [0] Configuration key name and
          [1] Optional default value to return if the key isn't found. If not given, a ConfigError will be raised.
        :rtype : V
        :return Configuration value corresponfing to the name or the default.
        """
        # Sort the arguments
        default = None
        default_given = False
        if type(key) is tuple:
            key_name = key[0]
            if len(key) > 1:
                default = key[1]
                default_given = True
        # If key is not a tuple, consider it a scalar [string] key name
        else:
            key_name = key

        # Try to fetch a key
        if key_name in self:
            return dict.__getitem__(self, key_name)
        # We don't have the key. If a default was given, return it
        elif default_given:
            return default
        # Otherwise raise an exception
        else:
            raise errors.ConfigError('The key named "{}" is not found in the configuration.'.format(key_name))

    def __setitem__(self, key, value):
        """Override the inherited setter to convert incoming dict values into Config instances."""
        if type(value) is dict:
            value = Config(value)
        dict.__setitem__(self, key, value)

    def lines(self, key: str) -> io.StringIO:
        """Return a configuration text value as an StringIO object by given key.
        :param key Name of the key to retrieve.
        """
        return io.StringIO(self[key])

    def lines_list(self, key: str) -> list:
        """Return a configuration text value as a list of strings without linebreaks.
        :param key Name of the key to retrieve.
        """
        return [line.rstrip('\r\n') for line in self.lines(key)]

    def update(self, *args, **kwargs):
        """Override to provide proper setter calls, also for the constructor."""
        # Process positional arguments (a single iterable is allowed)
        if args:
            if len(args) > 1:
                raise TypeError("update expected at most 1 arguments, got %d" % len(args))
            for k, v in dict(args[0]).items():
                self[k] = v

        # Process keyword arguments
        for k, v in kwargs.items():
            self[k] = v

