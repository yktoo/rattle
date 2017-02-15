from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Allows to execute an SQL query and fetch data from a database.

    Relevant configuration entries:
        output_param     -- Name of the parameter used for returning result data. Optional, default is 'data'.
        database         -- Name of the target database connection. Can refer to handler's own configuration parameters
                            in the form '{name}'.
        field_delimiter  -- String to be used as field delimiter in the output text. Optional, default is empty string.
        record_delimiter -- String to be used as record delimiter in the output text. Optional, default is the new line
                            character.
        col_headers      -- Boolean, if True, outputs column headers as the first record, separated by field_delimiter.
                            Optional, default is False.
        quotechar        -- Quote character for field values and column names. Optional, default is None.
        sql              -- SQL query. May contain parameter references in the form ':name'.
        params           -- Array of parameter definitions. Optional. Each element is an object consisting of:
            name             -- Parameter name.
            value            -- Parameter value. Can refer to handler's own configuration parameters in the form
                                '{name}'.
    """

    QUOTE_OPEN  = {None: '', '(': '(', '[': '[', '{': '{', '<': '<'}
    QUOTE_CLOSE = {None: '', '(': ')', '[': ']', '{': '}', '<': '>'}

    def run(self, config):
        """Override the abstract method of the base class."""
        # Get attributes from config
        output_param  = config['output_param',     'data']
        db_name       = config['database']
        fld_delimiter = config['field_delimiter',  '']
        rec_delimiter = config['record_delimiter', '\n']
        col_headers   = config['col_headers',      False]
        quotechar     = config['quotechar',        None]
        sql           = config['sql']
        params        = config['params',           None]

        # Substitute params in the DB connection and find it
        db_name = db_name.format(**config)
        db_conn = context.get_db_connection(db_name)

        # Prepare quote strings
        qopen  = self.QUOTE_OPEN [quotechar] if quotechar in self.QUOTE_OPEN  else quotechar
        qclose = self.QUOTE_CLOSE[quotechar] if quotechar in self.QUOTE_CLOSE else quotechar

        # Prepare parameters, if needed
        db_params = {}
        if params is not None:
            for param in params:
                p_name  = param['name']
                p_value = param['value']
                db_params[p_name] = p_value.format(**config)

        # Execute the query
        cur = db_conn.cursor()
        records = []
        try:
            cur.execute(sql, db_params)

            # Output column headers, if needed
            if col_headers:
                records.append(fld_delimiter.join([qopen + d[0] + qclose for d in cur.description]))

            # Read the returned data
            for record in cur:
                records.append(fld_delimiter.join([qopen + str(v) + qclose for v in record]))
        finally:
            cur.close()

        logger.log('Done. Read {} rows from {}'.format(len(records), db_name))
        return {output_param: rec_delimiter.join(records) + rec_delimiter}
