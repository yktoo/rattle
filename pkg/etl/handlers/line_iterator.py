from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Iterates through lines in the data and invokes a handler on each of them.

    Relevant configuration entries:
        input_param        -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_param       -- Name of the parameter used for returning result data. Optional, default is 'data'.
        passthrough_params -- Array specifying names of configuration params to be passed-through to child handler(s).
                              Optional.
        chomp              -- Boolean, whether to strip the terminating line-break. Optional, default is True.
        skip_blank_lines   -- Boolean, whether to skip invoking handler for blank lines (influenced by 'chomp'). Optional,
                              default is True.
        handler            -- Handler configuration (see context.invoke_handler() for details). Handler's configuration
                              will be amended with the elements:
            <output_param>       -- Line text
            <passthrough_params> -- All the parameters specified in the 'passthrough_params' list.
    """
    def run(self, config):
        """Override the abstract method of the base class."""
        # Fetch the config parameters
        input_param        = config['input_param',        'data']
        output_param       = config['output_param',       'data']
        passthrough_params = config['passthrough_params', None]
        chomp              = bool(config['chomp',            True])
        skip_blank_lines   = bool(config['skip_blank_lines', True])

        # Prepare child params
        if passthrough_params is None:
            sub_params = {}
        else:
            sub_params = {k: config[k] for k in passthrough_params}

        # Read the input data
        line_num = 0
        for line in config.lines(input_param):
            # Strip the linebreak if needed
            if chomp:
                line = line.rstrip('\r\n')

            # Invoke the handler
            if not skip_blank_lines or len(line) > 0:
                line_num += 1
                logger.log('Processing line #{}'.format(line_num))
                sub_params[output_param] = line
                context.invoke_handler(config['handler'], sub_params)
