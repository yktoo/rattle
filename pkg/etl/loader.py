#!/usr/bin/env python3
"""
Declares the Loader class, a flexible loader driven by a JSON configuration file(s).

Configuration file
    The configuration file drives the entire program flow. This program requires a configuration file in JSON format
    [http://www.json.org/].

    At its top level, this file contains the following objects:

    * processes         Array   Mandatory. Array of objects, each defining a certain 'data integration process', by
                                providing the following elements:
        - name          String  Mandatory. Name of the process.
        - comment       String  Optional. Description of the process. Default is empty string.
        - stop_on_error Boolean Optional. Whether to terminate processing on an unhandled exception. Default is True.
        - handler       Handler Mandatory. Handler configuration (see context.invoke_handler() for details).

    * databases         Array   Mandatory if any handlers requiring a database connection are used. Each element is an
                                object describing a database connection by providing the following elements:
        - name          String  Mandatory. Unique database name, used as a reference in other places.
        - connection    String  Mandatory. DB connection string in the format '<driver_name>:<driver_specific_config>'.
                                Available drivers   Driver configuration format
                                -----------------   ---------------------------
                                oracle              host:port:sid
        - username      String  Mandatory. DB user name.
        - password      String  Mandatory. DB user password.

    * log               Object  Optional. Logging configuration, consisting of the following elements:
        - file          String  Optional. Name of the log file. If omitted, all the logging will be output to the
                                standard output (stdout) for messages with severities DEBUG and INFO, and to the
                                standard error (stderr) for messages with severities WARNING and ERROR.
        - verbose       Boolean Optional. Whether verbose logging must be used. In non-verbose mode messages with
                                DEBUG severity are not logged. Default is false. Note: this setting can be overridden
                                on the command line with the `--verbose`/`--no-verbose` options.
    * globals           Object  Optional. Object defining global configuration parameters that will be passed to every
                                handler (but can be overridden by scoped parameters).
"""
import sys
from . import logger
from . import context
from . import config


class Loader(object):
    """A flexible data loader driven by a configuration file, that is passed in the constructor."""

    def __init__(self, config_file_name: str, verbose: [bool, None], dry_run: bool, global_overrides: dict):
        """Constructor.
        :param config_file_name: Path to the configuration file in JSON format.
        :param verbose: Whether verbose logging is to be used. If not None, overrides logging verbosity setting given in
            the configuration file.
        :param dry_run: Whether to avoid making changes to DB.
        :param global_overrides: Dictionary of global parameters that take precedence over ones defined in the 'globals'
            config object.
        """
        self.failed_processes = []
        self.cnt_proc_total = 0
        self.cnt_proc_ok    = 0
        self.cnt_proc_fail  = 0
        # Initialise the context
        context.initialise(config_file_name, verbose, dry_run, global_overrides)

    def run(self):
        """The main function of the loader. Perform the load according to the provided configuration.
        :return True if all processes finished successfully, False otherwise
        """
        logger.info('Starting the load.')

        # Reset stats
        self.failed_processes = []
        self.cnt_proc_total = 0
        self.cnt_proc_ok    = 0
        self.cnt_proc_fail  = 0

        # Iterate through processes
        for process_conf in context.get_config()['processes']:
            self.run_process(process_conf)

        # Output a summary
        logger.info(
            'Load finished, ran {} processes, {} succeeded, {} failed.'.format(
                self.cnt_proc_total, self.cnt_proc_ok, self.cnt_proc_fail))
        if self.failed_processes:
            logger.warning('Failed processes: ' + ', '.join(self.failed_processes))

        return self.cnt_proc_fail == 0

    def run_process(self, process_conf: config.Config) -> bool:
        """Run a single process.
        :param process_conf Dictionary describing process configuration.
        :return True if process finished successfully, False otherwise
        """
        self.cnt_proc_total += 1
        # Fetch config parameters
        name          = process_conf['name']
        comment       = process_conf['comment', '']
        stop_on_error = process_conf['stop_on_error', True]
        handler_conf  = process_conf['handler']

        # Log
        logger.separator()
        logger.info('Running process "{}"{}'.format(
            name,
            (' (' + comment + ')' if comment != '' else '')))

        # Run the handler
        successful = False
        try:
            context.invoke_handler(handler_conf)
            self.cnt_proc_ok += 1
            successful = True

        # Catch and log any exceptions
        except Exception as e:
            self.cnt_proc_fail += 1
            self.failed_processes.append(name)
            logger.error('Exception {}: {}'.format(str(type(e)), str(e)))
            if stop_on_error:
                logger.info('Error occurred, exiting.')
                sys.exit(1)

        return successful
