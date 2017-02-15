from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Writes provided data into a file.

    Relevant configuration entries:
        input_param -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_file -- Full path to the output file. Can contain references to configuration parameters in the form
                       "{param_name}".
        append      -- Boolean, whether to overwrite (False) or append (True) the file if it exists. Optional, default
                       is False.
    """
    def run(self, config):
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param = config['input_param', 'data']
        output_file = config['output_file']
        data        = config[input_param]
        append      = bool(config['append', False])

        # Substitute config params and canonicalise
        output_file = context.get_absolute_file_name(output_file.format(**config))

        # Write the data into the file
        with open(output_file, 'a' if append else 'w', encoding='utf-8') as f:
            f.write(data)

        logger.info('File {} is {} ({} bytes).'.format(output_file, 'appended' if append else 'written', len(data)))
