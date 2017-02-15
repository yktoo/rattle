import re
from etl import logger
from etl.handlers import base


class Handler(base.Handler):
    """Regex matcher, captures matches in the input data based on regex patterns and returns them as lines via the
    specified config parameters.

    Relevant configuration entries:
        input_param  -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_param -- Name of the parameter used for returning result data. Optional, default is 'data'.
        regex        -- Regular expression to run against the data.
        group_num    -- Number of capture group containing the result of the match (0 for the whole match, 1 for the
                        first captured expression and so on).
        unique       -- Boolean, specifies where the list of matches has to be deduplicated before handler invocation.
                        Optional, default is False.

    :return dict containing 'data' parameter.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param  = config['input_param',  'data']
        output_param = config['output_param', 'data']
        data         = config[input_param]
        regex        = config['regex']
        group        = int(config['group_num'])
        unique       = bool(config['unique', False])

        # Collect all matches
        matches = [match.group(group) for match in re.finditer(regex, data)]

        # Deduplicate matches if needed, keeping the order
        if unique:
            unique_matches = []
            for m in matches:
                if m not in unique_matches:
                    unique_matches.append(m)
            matches = unique_matches

        logger.log("Found {}{} match(es)".format(len(matches), ' unique' if unique else ''))

        # Return the result
        return {output_param: '\n'.join(matches) + '\n'}
