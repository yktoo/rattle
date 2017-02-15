from etl import logger
from etl.handlers import base


class Handler(base.Handler):
    """Sorts lines in the data and returns the result via the specified config parameters.

    Relevant configuration entries:
        input_param  -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_param -- Name of the parameter used for returning result data. Optional, default is 'data'.
        reverse      -- Boolean, whether to reverse-sort lines. Optional, default is False.

    :return dict containing 'data' parameter.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param  = config['input_param',  'data']
        output_param = config['output_param', 'data']

        # Read the input data
        lines = sorted(config.lines_list(input_param), reverse=bool(config['reverse', False]))
        logger.log("Sorted {} lines".format(len(lines)))

        # Return the result
        return {output_param: '\n'.join(lines) + '\n'}
