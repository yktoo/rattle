from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Reads in a text file and returns its contents.

    Relevant configuration entries:
        file_name    -- Full name of the file. Can contain references to configuration parameters in the form
                        '{param_name}'.
        output_param -- Name of the parameter used for returning result data. Optional, default is 'data'.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        file_name    = config['file_name']
        output_param = config['output_param', 'data']

        # Substitute config params and canonicalise
        file_name = context.get_absolute_file_name(file_name.format(**config))

        # Load the file
        with open(file_name) as f:
            data = f.read()

        # Return the result
        logger.info('Loaded {} characters from {}'.format(len(data), file_name))
        return {output_param: data}
