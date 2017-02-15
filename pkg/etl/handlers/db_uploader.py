import csv

from etl.db.connection import DBConnection
from etl.db.array_inserter import DBArrayInserter
from etl import errors
from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Generic handler that allows to upload tabular data, either fixed-width or delimited, to a DB table. Input records
    must be separated by newline character.

    Relevant configuration entries:
        input_param     -- Name of the parameter used for reading input data. Optional, default is 'data'.
        format          -- Format of the input data, either 'fixed' (fixed-width fields) or 'delimited' (fields are
                           delimited with 'delimiter').
        delimiter       -- Field delimiter character. Mandatory if 'format' is 'delimited', otherwise ignored.
        quotechar       -- Quote character. Optional if 'format' is 'delimited', otherwise ignored.
        start_line      -- Integer, number of the line to start data import with (1-based). Optional, default is 1.
        target_database -- Name of the target database connection. Can refer to handler's own configuration parameters
                           in the form '{name}'.
        target_table    -- Name of the target table, possibly with schema name before it.
        truncate_target -- Boolean, whether or not to truncate the target table before the load. Optional, False by
                           default
        column_mappings -- Array of objects describing column mappings, each object consisting of:
            name            -- (Display) name of the column.
            datatype        -- Datatype of the column, one of "string", "number", "integer", "datetime". Mandatory if
                               'source_pos'/'source_index' is specified.
            length          -- Data length, integer in the range 1..4000. Mandatory for columns of datatype "string",
                               ignored for all other datatypes.
            truncate        -- Whether to truncate data whose length exceeds length value. When such a value is
                               encountered, if truncate is true, it gets shortened to the value of length; if truncate
                               is false, in error is raised and processing fails. Optional for columns of datatype
                               "string", ignored for all other datatypes.
            source_pos      -- Column boundary specification in the format '<left_pos>:<right_pos>', where <left_pos>
                               and <right_pos> are 1-based column left and right boundaries, respectively. For example,
                               for the string 'abc defg' column 1 has boundaries '1:3' and column 2 - '5:8'.
                               * Fixed-width files: optional, if omitted, 'target_expr' must represent a constant
                                 expression or a built-in database function
                               * Delimited files: ignored.
            source_index    -- 0-based index of the source column in the data.
                               * Fixed-width files: ignored.
                               * Delimited files: optional, if omitted, 'target_expr' must represent a constant
                                 expression or a built-in database function.
            source_trim     -- Trimming (whitespace removal) mode for source values, one of:
                               * 'none'  - no trimming will occur;
                               * 'left'  - trim leading whitespace;
                               * 'right' - trim trailing whitespace;
                               * 'both'  - trim leading and trailing whitespace.
                               Optional, default is 'none'.
            source_format   -- Optional, format for source data for the 'datetime' datatype.
            target_column   -- Name of the column in the target_table.
            target_expr     -- Expression to use for the inserted value. Mandatory unless source_pos/source_index is
                               provided. If source value (source_pos/source_index) is provided, can refer to the source
                               value as '{value}' (if omitted, the source value us used as-is), otherwise to the current
                               target row number (1-based) as '{rownum}'. In both cases can refer to config parameters
                               as '{param_name}'.
    """
    @staticmethod
    def get_inserter(
            connection: DBConnection, target_table: str, column_mappings: dict, fmt_fixed: bool,
            fmt_delimited: bool, config: dict) -> DBArrayInserter:
        """Creates an insert SQL statement for the specified table and columns and returns a DBArrayInserter object for
        it.
        """
        col_names   = []
        col_values  = []
        col_lengths = []
        idx = 0
        for cm in column_mappings:
            idx += 1
            col_name    = cm['name']
            target_expr = cm['target_expr', None]

            # Add target column name
            col_names.append(cm['target_column'])

            # Get a parameter placeholder
            val = connection.get_param_placeholder(idx)

            # If source is given
            if (fmt_fixed and 'source_pos' in cm) or (fmt_delimited and 'source_index' in cm):
                # Also validate the datatype
                datatype = cm['datatype', cm]
                if datatype == 'string':
                    length = int(cm['length'])
                    if not 1 <= length <= 4000:
                        raise errors.ConfigError(
                            'Invalid length for the column "{}": {} (must be between 1 and 4000)'.format(
                                col_name, length))
                elif datatype == 'number' or datatype == 'integer':
                    length = DBConnection.NUMBER
                elif datatype == 'datetime':
                    if 'source_format' in cm:
                        val = connection.get_datetime_expression(val, "'{}'".format(cm['source_format']))
                    length = 30
                else:
                    raise errors.ConfigError('Invalid datatype for the column "{}": "{}"'.format(col_name, datatype))

                # If the expression is given, apply it to the placeholder (enrich with config params)
                if target_expr is not None:
                    conf_copy = config.copy()
                    conf_copy['value'] = val
                    val = target_expr.format(**conf_copy)

                # Add target value length
                col_lengths.append(length)

            # Otherwise target expression is mandatory
            else:
                if target_expr is None:
                    raise errors.ConfigError(
                        'Column "{}": target_expr must be specified unless {} is given'.format(
                            col_name, 'source_pos' if fmt_fixed else 'source_index'))

                # If the target expression uses {rownum}, add a placeholder to config
                conf_copy = config.copy()
                if '{rownum}' in target_expr:
                    conf_copy['rownum'] = val

                # Enrich the expression with config parameters
                val = target_expr.format(**conf_copy)

            # Add target value placeholder or expression
            col_values.append(val)

        # Construct the final statement
        stmt = 'insert /*+ append */ into {}({}) values({})'.format(
            target_table, ', '.join(col_names), ', '.join(col_values))

        # Construct an array inserter, if we're not in dry-run mode
        if context.dry_run_mode:
            return None
        else:
            return DBArrayInserter(connection, stmt, col_lengths, False)

    def run(self, config):
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param = config['input_param',  'data']
        data        = config.lines(input_param)
        delimiter = None
        quotechar = None

        # Get and validate data format
        data_format = config['format']
        fmt_fixed     = data_format == 'fixed'
        fmt_delimited = data_format == 'delimited'
        if not fmt_fixed and not fmt_delimited:
            raise errors.ConfigError('Invalid format value: "{}".'.format(data_format))
        if fmt_delimited:
            delimiter = config['delimiter']
            quotechar = config['quotechar', None]

        # Fetch other config attributes
        start_line      = int(config['start_line', 1])
        target_database = config['target_database']
        target_table    = config['target_table']
        truncate_target = bool(config['truncate_target', False])
        column_mappings = config['column_mappings']

        # Substitute params in the DB connection
        target_database = target_database.format(**config)
        logger.log(context.dry_run_prefix + 'Loading data to {}@{}'.format(target_table, target_database))

        # Find the DB connection
        db_conn = context.get_db_connection(target_database)

        # Truncate the target table, if required
        if truncate_target:
            if not context.dry_run_mode:
                db_conn.execute('truncate table {} drop storage'.format(target_table))
            logger.log(context.dry_run_prefix + 'Table {}@{} is truncated'.format(target_table, target_database))

        # Create an inserter
        inserter = self.get_inserter(db_conn, target_table, column_mappings, fmt_fixed, fmt_delimited, config)

        # Fixed-width file: use the input data as is
        if fmt_fixed:
            input_data = data

        # Delimited file: open the input data as a CSV file
        else:
            args = {'delimiter': delimiter, 'strict': True}
            if quotechar is not None:
                args['quotechar'] = quotechar
            input_data = csv.reader(data, **args)

        # Iterate through the data
        count_src_lines = 0
        count_tgt_rows = 0
        for src_row in input_data:
            # Skip up to start_line
            count_src_lines += 1
            if count_src_lines < start_line:
                continue

            # Fetch data values
            try:
                target_row = []
                for cm in column_mappings:
                    # If a source value is used
                    if (fmt_fixed and 'source_pos' in cm) or (fmt_delimited and 'source_index' in cm):
                        col_name = cm['name']
                        datatype = cm['datatype']
                        trim     = cm['source_trim', 'none']

                        # Fixed-width
                        if fmt_fixed:
                            pos = cm['source_pos'].partition(':')
                            # Validate the position format
                            if pos[0] == '' or pos[2] == '':
                                raise errors.ConfigError('Invalid position specifier "{}" for column "{}"'.format(
                                    cm['source_pos'], col_name))
                            # Validate left boundary
                            try:
                                pos_l = int(pos[0]) - 1
                            except ValueError as e:
                                raise errors.ConfigError('Left boundary specification for column "{}": {}'.format(
                                    col_name, str(e)))
                            if pos_l < 0:
                                raise errors.ConfigError('Left boundary must be positive (column "{}")'.format(
                                    col_name))
                            # Validate right boundary
                            try:
                                pos_r = int(pos[2])
                            except ValueError as e:
                                raise errors.ConfigError('Right boundary specification for column "{}": {}'.format(
                                    col_name, str(e)))
                            if pos_r <= pos_l:
                                raise errors.ConfigError(
                                    'Right boundary must be greater than or equal to the left one (column "{}")'.format(
                                        col_name))
                            # Chomp
                            src_row = src_row.rstrip('\r\n')
                            # Extract column value
                            value = src_row[pos_l:pos_r]

                        # Delimited
                        else:
                            value = src_row[int(cm['source_index'])]

                        # Apply trimming
                        if trim == 'none':
                            pass
                        elif trim == 'left':
                            value = value.lstrip()
                        elif trim == 'right':
                            value = value.rstrip()
                        elif trim == 'both':
                            value = value.strip()
                        else:
                            raise errors.ConfigError('Invalid trim value for column "{}": "{}"'.format(col_name, trim))

                        # All types: handle null values
                        val_len = len(value)
                        if val_len == 0:
                            value = None
                        # String: validate value length
                        elif datatype == 'string':
                            max_len = int(cm['length'])
                            # If the length exceeds the allowed size
                            if val_len > max_len:
                                # No truncation - raise an error
                                if not bool(cm['truncate', False]):
                                    raise errors.DataError(
                                        'String column "{}": value length ({}) exceeds allowed maximum ({})'.format(
                                            col_name, val_len, max_len))
                                # Otherwise truncate the value
                                value = value[:max_len]
                        # Integer: convert to actual int
                        elif datatype == 'integer':
                            try:
                                value = int(value)
                            except ValueError as e:
                                raise errors.DataError('Integer column "{}": {}'.format(col_name, str(e)))
                        # Number: convert to actual number
                        elif datatype == 'number':
                            try:
                                value = float(value)
                            except ValueError as e:
                                raise errors.DataError('Float value error for column "{}": {}'.format(col_name, str(e)))

                        # Add the value to the target row
                        target_row.append(value)

                    # Otherwise we're using a target expression
                    else:
                        target_expr = cm['target_expr']

                        # If it uses row number value, add it to the row
                        if '{rownum}' in target_expr:
                            target_row.append(count_tgt_rows + 1)

            # Reraise ConfigErrors as is
            except errors.ConfigError:
                raise

            # Assume all other errors are coming from the data
            except Exception as e:
                raise errors.DataError('Input data error at line {}: {}'.format(count_src_lines, str(e)))

            # Push the row to the target table (unless we're in dry-run mode)
            if not context.dry_run_mode:
                inserter.push_row(target_row)
            count_tgt_rows += 1

        # Finalise
        if not context.dry_run_mode:
            inserter.flush()
            db_conn.commit()
        logger.info(context.dry_run_prefix + 'Loading {}@{} finished, read {} rows, inserted {} rows.'.format(
            target_table, target_database, count_src_lines, count_tgt_rows))
