"""
Declaration of an application context. Provides access to application-wide configuration and database connection pool.
"""

import atexit
import os
import importlib
import json
import base64
from . import errors
from . import logger
from . import config
from .db.connection import DBConnection
from .handlers.base import Handler

_config = None           # Private configuration collection
_connections = {}        # Private database connection pool
_globals = {}            # Private global configuration object
_config_file_stack = []  # Stack of loaded config file paths, with at least the main config file at the bottom

verbose_mode = False     # Verbose mode

dry_run_mode = False     # Dry-run mode
dry_run_prefix = ''      # Prefix to be used in logging of operations affected by the dry-run flag


def _check_initialised(initialised: bool=True):
    """Raises a LogicError if the initialised state is not correct.

    :param initialised If False, raises an exception if the context is already initialised, otherwise raises an
        exception if it's not initialised yet.
    """
    global _config
    if initialised:
        if _config is None:
            raise errors.LogicError("Context hasn't been initialised yet.")
    else:
        if _config is not None:
            raise errors.LogicError("Context has already been initialised.")


def _init_logging(b_verbose: bool):
    """Initialise logger properties from the provided configuration. Is called internally from initialise().
    :param b_verbose Verbosity value passed on the command line. None if nothing was specified.
    """
    global verbose_mode
    verbose_mode = b_verbose
    # If logger config is provided
    log_conf = _config['log', None]
    if log_conf is not None:
        # If verbosity isn't overridden
        if verbose_mode is None:
            verbose_mode = log_conf['verbose', False]
        # Set up logfile
        logger.set_log_file(log_conf['file', None])

    # Set up logger verbosity
    if verbose_mode:
        logger.minimum_severity = logger.DEBUG


def _load_config(config_file_name: str):
    """Load, parse and return JSON configuration from a file specified by name.
    :param config_file_name: Name of the JSON configuration file, either absolute or relative to the last loaded file's
        location.
    """
    global _config_file_stack

    # Convert the file name into an absolute one
    config_file_name = get_absolute_file_name(config_file_name)

    # Open and read in the file
    with open(config_file_name, 'r') as cf:
        conf = json.load(cf, object_hook=lambda dct: config.Config(dct))
    logger.log('Loaded configuration file ' + config_file_name)

    # Push the name of the file into the stack
    _config_file_stack.append(config_file_name)
    return conf


def _unload_config():
    """Must be called whenever the file last loaded by _load_config() is not needed anymore."""
    global _config_file_stack
    # Remove the last loaded file's name from the stack
    _config_file_stack.pop()


def _load_db_connection(file_name: str):
    """Load, parse and return JSON DB connection configuration from a file specified by name.
    :param file_name: Name of the JSON DB connection configuration file, either absolute or relative to the last loaded
                      configuration file's location.
    """
    # Convert the file name into an absolute one
    file_name = get_absolute_file_name(file_name)

    # Open and read in the file
    with open(file_name, 'r') as cf:
        conf = json.load(cf, object_hook=lambda dct: config.Config(dct))
    logger.log('Loaded DB connection configuration file ' + file_name)

    return conf


def _run_handler(own_conf, external_conf, pipeline_conf):
    """Load, instantiate and run a handler or a list of handlers according to the specified configurations.
    :param own_conf: Own handler configuration.
    :param external_conf: Configuration passed from the calling code, if any, otherwise None.
    :param pipeline_conf: Pipeline (dynamic) configuration if the handler is a part of a pipeline, otherwise None.
    """
    # If config is a string, we assume this is a path to an include-configuration file
    conf_file_loaded = False
    if type(own_conf) is str:
        # Load the referenced file and replace the value of the configuration object by it
        own_conf = _load_config(own_conf)
        conf_file_loaded = True

    try:
        # If it's a single object, process it
        if type(own_conf) is config.Config:

            # If it's a handler configuration
            if 'module' in own_conf:
                # Fetch handler details
                handler_module = own_conf['module']
                if '.' not in handler_module:
                    handler_module = 'etl.handlers.' + handler_module
                handler_clsname = own_conf['class',   'Handler']
                handler_comment = own_conf['comment', '']

                # Construct an individual config copy for the handler
                # -- Start with the global items
                handler_conf = config.Config(_globals)
                # -- Update it with external items, if any
                if external_conf is not None:
                    handler_conf.update(external_conf)
                # -- Local handler items override them
                handler_conf.update(own_conf)
                # -- Pipeline config has the highest precedence since it's dynamic
                if pipeline_conf is not None:
                    handler_conf.update(pipeline_conf)

                # Beautify handler's comment, if any
                if handler_comment != '':
                    handler_comment = ' (' + handler_comment.format(**handler_conf) + ')'
                logger.log(
                    'Invoking handler {}.{}{}'.format(handler_module, handler_clsname, handler_comment))

                # Import the corresponding handler module
                handler_module = importlib.import_module(handler_module)

                # Find handler class object
                handler_class = getattr(handler_module, handler_clsname)
                assert issubclass(handler_class, Handler)

                # Construct and run the handler
                result = handler_class().run(handler_conf)

                # If we're on a pipeline, return output parameter values onto it
                if pipeline_conf is not None and result is not None:
                    pipeline_conf.update(result)

            # Otherwise it's a parameter block: publish its parameters on the pipeline
            elif pipeline_conf is not None:
                pipeline_conf.update(own_conf)

        # If it's a list of handlers, run them in sequence
        elif type(own_conf) is list:

            # If there's no pipeline yet, start a new one here
            sub_pipeline_conf = pipeline_conf if pipeline_conf is not None else config.Config()

            # Iterate through the child objects
            for sub_conf in own_conf:
                _run_handler(sub_conf, external_conf, sub_pipeline_conf)

        # Not a config or list means a misconfiguration
        else:
            raise errors.ConfigError(
                'Handler configuration must be a string, an object or an array, not "{}"'.format(str(type(own_conf))))

    finally:
        # If we loaded config from a file, make sure it's properly unloaded
        if conf_file_loaded:
            _unload_config()


def initialise(config_file_name: str, b_verbose: bool, b_dry_run: bool, global_overrides: dict):
    """Initialise the context with the specified configuration.
    :param config_file_name: Path to the config file.
    :param b_verbose: Verbosity override for the logging.
    :param b_dry_run: Whether to avoid making changes to DB.
    :param global_overrides: Dictionary of global parameters that take precedence over ones defined in the 'globals'
        config object.
    """
    global _config, _globals, dry_run_mode, dry_run_prefix

    # Make sure the context hasn't been initialised yet
    _check_initialised(False)

    dry_run_mode = b_dry_run

    # Canonicalize the file name, as _load_config() always expects the main file to be with absolute path
    config_file_name = os.path.realpath(config_file_name)

    # Read in and parse the JSON-formatted config
    _config = _load_config(config_file_name)

    # Prepare global config
    _globals = _config['globals', config.Config()]
    assert isinstance(_globals, config.Config)

    # Override config's globals with external ones
    _globals.update(global_overrides)

    # Initialise the logger
    _init_logging(b_verbose)

    # Log basic info
    logger.info('Configuration file: {}'.format(config_file_name))
    if dry_run_mode:
        dry_run_prefix = '[DRY-RUN] '
        logger.info('Running in the dry-run mode.')


def get_absolute_file_name(file_name: str) -> str:
    """Convert relative file name into an absolute one using the last loaded config file's path. If file_name is already
    absolute, return it as is.

    :param file_name: File name to convert to absolute.
    :return Absolute file name.
    """
    global _config_file_stack

    # If the file name is not absolute, it's considered relative to the last loaded config file's location
    if not os.path.isabs(file_name):
        # If no file was loaded before, we've got a problem
        if len(_config_file_stack) == 0:
            raise errors.LogicError(
                'Cannot translate relative file path "{}" out-of-context'.format(file_name))
        file_name = os.path.realpath(os.path.join(os.path.dirname(_config_file_stack[-1]), file_name))
    return file_name


def get_config() -> config.Config:
    """Return the configuration collection associated with the context."""
    _check_initialised()
    return _config


def get_db_connection(name: str) -> DBConnection:
    """Return a ready-for-use DBConnection object by its name. The name must be defined in the configuration, otherwise
    an exception is raised.
    :param name Name of the database connection as defined in the configuration.
    """
    global _config, _connections, _globals
    _check_initialised()
    # If the DB connection by that name doesn't exist yet
    if name not in _connections:
        # Find the connection definition in the config
        db_name_found = False
        db_conf = None
        for db_conf in _config['databases']:
            # If the configuration is not an object, it's a misconfiguration
            if type(db_conf) is not config.Config:
                raise errors.ConfigError(
                    'DB connection configuration must be an object, not "{}"'.format(str(type(db_conf))))

            # Check if that's the connection we're looking for
            if db_conf['name'] == name:
                db_name_found = True
                break

        # Failed to find a connection by the requested name
        if not db_name_found:
            raise errors.ConfigError('Database connection named "{}" is not found.'.format(name))

        # If the entry contains 'file_name', it's a path to an external connection description file
        if 'file_name' in db_conf:
            # Load the referenced file and replace the config values
            ext_conf = _load_db_connection(db_conf['file_name'].format(**_globals))
            for k in ['connection', 'username', 'password']:
                db_conf[k] = ext_conf[k]

        # Check if the password is encoded
        password = db_conf['password']
        if password[0:7] == 'BASE64:':
            password = base64.b64decode(password[7:]).decode()

        # Create a new connection
        conn = DBConnection(db_conf['connection'], db_conf['username'], password)
        logger.info(
            'Established DB connection to {}@{} as "{}"'.format(db_conf['username'], db_conf['connection'], name))

        # Store the connection in the pool
        _connections[name] = conn
    # Connection already exists
    else:
        conn = _connections[name]
    return conn


def invoke_handler(own_config, external_config=None):
    """Loads, instantiates and runs a handler or several handlers defined by the configuration.
    :param own_config Handler configuration, either a configuration object, or an array of such objects (to
        chain handlers). Each configuration object can contain either:
            #include -- name of the file to replace this object,
        or the following elements:
            module  -- Python module containing handler code. Can be either a fully qualified name that includes package
                       name, or a simple name that is considered one of the standard library handlers (i.e. etl.handlers
                       package).
            class   -- Handler class to instantiate. Its method run(config) is then called. Optional, default is
                       'Handler'.
            comment -- Additional info about the step the handler executes. Optional. Can contain references to other
                       config parameters in the form {param_name}
    :param external_config External parameters for the handler(s)
    """
    _run_handler(own_config, external_config, None)


def teardown():
    """Cleanup procedure for the module."""
    global _config, _connections, _globals, _config_file_stack
    # If context has been initialised
    if _config is not None:
        # Delete all created DB connection
        del _connections
        _connections = {}
        # Drop the config
        _config = None
        _globals = {}
        # Unload the config file
        _unload_config()
    # Make sure the file name stack is empty
    _config_file_stack = []


# Register a shutdown procedure
atexit.register(teardown)
