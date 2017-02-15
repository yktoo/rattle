import io
from etl import logger
from etl.handlers import base


class Handler(base.Handler):
    """Merges every N lines into one, with an optional delimiter. This is a pipeline-type handler that receives and
    returns the data via the specified config parameters.

    Relevant configuration entries:
        input_param         -- Name of the parameter used for reading input data. Optional, default is 'data'.
        output_param        -- Name of the parameter used for returning result data. Optional, default is 'data'.
        start_line          -- Integer, number of the line to start data import with (1-based). Optional, default is 1.
        num_lines_to_merge  -- Number of lines to concatenate into one.
        trim_lines          -- Boolean, whether to trim merged lines. Optional, default is False.
        skip_blank_lines    -- Boolean, whether to skip blank lines (if True, blank lines are not counted for merging).
                               Optional, default is False. NB: detection of blank lines is influenced by 'trim_lines'.
        delimiter           -- Delimiter string to insert between concatenated strings. Optional, default is "".
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param      = config['input_param',  'data']
        output_param     = config['output_param', 'data']
        src_data         = config.lines(input_param)
        start_line       = int(config['start_line', 1])
        merge_cnt        = int(config['num_lines_to_merge'])
        trim_lines       = bool(config['trim_lines', False])
        skip_blank_lines = bool(config['skip_blank_lines', False])
        delimiter        = config['delimiter', '']

        # Iterate through data lines
        tgt_data = io.StringIO()
        count_src_lines = 0
        count_tgt_lines = 0
        count_merged    = 0
        merged_line = ''
        for src_line in src_data:
            # Skip up to start_line
            count_src_lines += 1
            if count_src_lines < start_line:
                continue

            # Strip all whitespace if needed, otherwise only the terminating linebreak
            line = src_line.strip() if trim_lines else src_line.rstrip('\r\n')

            # If the line is blank and we're skipping them
            if skip_blank_lines and line == '':
                continue

            # Merge lines
            count_merged += 1
            if count_merged > 1:
                merged_line += delimiter
            merged_line += line

            # If merge threshold is reached
            if count_merged == merge_cnt:
                tgt_data.write(merged_line + '\n')
                count_tgt_lines += 1
                count_merged = 0
                merged_line = ''

        # Flush the possible remaining merged lines
        if count_merged > 0:
            tgt_data.write(merged_line + '\n')
            count_tgt_lines += 1

        logger.log('Done. Input: {} lines, output: {} lines.'.format(count_src_lines, count_tgt_lines))

        # Return the result
        return {output_param: tgt_data.getvalue()}
