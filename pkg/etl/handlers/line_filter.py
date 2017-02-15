import re
from etl import logger
from etl.handlers import base


class Handler(base.Handler):
    """Filters lines in the input data based on specified criteria and returns the result.

    Relevant configuration entries:
        input_param      -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_param     -- Name of the parameter used for returning lines that pass the filter. Optional, default is
                            'data'.
        rejected_param   -- Name of the parameter used for returning lines that don't pass the filter. Optional, if not
                            specified, the rejected lines are discarded.
        start_line       -- Integer, number of the line to start data reading with (1-based). Optional, default is 1.
                            NB: counting for the start line ignores the 'skip_blank_lines' setting.
        skip_blank_lines -- Boolean, whether to skip blank lines. Optional, default is False.
        criteria         -- A filtering criterion or an array of such criteria. Optional. If specified, only those input
                            lines that match ALL criteria are added to the output set. Each criterion is an object with
                            the following elements:
            search              -- Substring or regex pattern to match against each input line.
            is_regex            -- Boolean. Whether 'search' is a substring (is_regex=false) or a regular expression
                                   (is_regex=true) to match. Optional, default is false.
            substitute_params   -- Boolean. Whether 'search' should be searched for parameter substitutions in the form
                                   '{param_name}', whose occurrences will be replaced with respective parameter values.
                                   Optional, default is false.
            negate              -- Boolean. Whether lines matching this rule are to be included (negate=false) or
                                   excluded (negate=true) from the output set. Optional, default is false.

    :return dict containing 'data' parameter.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param      = config['input_param',    'data']
        output_param     = config['output_param',   'data']
        rejected_param   = config['rejected_param', None]
        start_line       = int(config['start_line', 1])
        skip_blank_lines = bool(config['skip_blank_lines', False])
        criteria         = config['criteria', None]

        # Convert a single criterion to a one-item list
        if criteria is not None and type(criteria) is not list:
            criteria = [criteria]

        # Process the input lines
        count_src_lines = 0
        tgt_lines = []
        rej_lines = []
        for line in config.lines_list(input_param):
            # Skip up to start_line
            count_src_lines += 1
            if count_src_lines < start_line:
                continue

            # Skip blank lines
            if skip_blank_lines and len(line) == 0:
                continue

            # Process criteria, if any
            do_include = True
            if criteria is not None:
                for criterion in criteria:
                    cr_search            = criterion['search']
                    cr_is_regex          = bool(criterion['is_regex',          False])
                    cr_substitute_params = bool(criterion['substitute_params', False])
                    cr_negate            = bool(criterion['negate',            False])
                    # Substitute params if needed
                    if cr_substitute_params:
                        cr_search = cr_search.format(**config)
                    # Run the matching
                    match = re.search(cr_search, line) is not None if cr_is_regex else cr_search in line
                    # If the matching failed (it's an XOR condition effectively)
                    if cr_negate == match:
                        do_include = False
                        break

            # Add an output line, if needed
            if do_include:
                tgt_lines.append(line)

            # Otherwise accumulate rejected line, if needed
            elif rejected_param is not None:
                rej_lines.append(line)

        # Log the stats and prepare the result
        result = {output_param: '\n'.join(tgt_lines) + '\n'}
        if rejected_param is None:
            logger.log("Read {} input lines, kept {} lines".format(count_src_lines, len(tgt_lines)))
        else:
            logger.log(
                "Read {} input lines, kept {}, rejected {} lines".format(
                    count_src_lines, len(tgt_lines), len(rej_lines)))
            result[rejected_param] = '\n'.join(rej_lines) + '\n'

        # Return the result
        return result
