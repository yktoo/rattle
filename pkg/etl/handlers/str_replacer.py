import re
from etl import logger
from etl.handlers import base


class Handler(base.Handler):
    """Replaces substring occurrences in the data. This is a pipeline-type handler that receives and returns the data
    via the specified config parameters.

    Relevant configuration entries:
        input_param  -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_param -- Name of the parameter used for returning result data. Optional, default is 'data'.
        rules        -- Array of entries describing replacement rules. Each entry is an object with the following
                        elements:
            search       -- Substring or pattern to search.
            replace      -- Substring to replace 'search'.
            count        -- Maximal number  of occurrences to replace. If 0, all occurrences are replaced. Optional,
                            default is 0.
            is_regex     -- Boolean. Whether 'search' is a regex to match. Optional, default is False.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param  = config['input_param',  'data']
        output_param = config['output_param', 'data']
        data         = config[input_param]
        rules        = config['rules']
        size_in = len(data)

        # Iterate through rules
        for rule in rules:
            search   = rule['search']
            replace  = rule['replace']
            count    = int(rule['count', 0])
            is_regex = bool(rule['is_regex', False])
            if is_regex:
                data = re.sub(search, replace, data, count)
            else:
                data = data.replace(search, replace, count if count > 0 else -1)

        logger.log('Done. Input: {} bytes, output: {} bytes.'.format(size_in, len(data)))

        # Return the result
        return {output_param: data}
