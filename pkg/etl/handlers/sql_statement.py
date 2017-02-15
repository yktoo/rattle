from etl import errors
from etl import logger
from etl import context
from etl.handlers import base


class Handler(base.Handler):
    """Allows to execute an SQL statement against the database.

    Relevant configuration entries:
        database    -- Name of the target database connection. Can refer to handler's own configuration parameters in
                       the form '{name}'.
        sql         -- SQL statement or an array of SQL statements to execute. Statements may contain parameter
                       references in the form ':name'.
        commit_stmt -- Statement commit policy. Optional, default is 'each'. Allowed values:
            'none'      -- Do not issue any implicit commits.
            'each'      -- Commit after each statement.
            'all'       -- Commit once after all statements.
        params      -- Array of parameter definitions. Optional. Each element is an object consisting of:
            name        -- Parameter name.
            value       -- Parameter value. Can refer to handler's own configuration parameters in the form '{name}'.
    """
    COMMIT_NONE = 0
    COMMIT_EACH = 1
    COMMIT_ALL  = 2

    def run(self, config):
        """Override the abstract method of the base class."""
        # Get attributes from config
        db_name     = config['database']
        sql         = config['sql']
        params      = config['params', None]
        commit_stmt = config['commit_stmt', 'each']

        if commit_stmt == 'none':
            commit_policy = self.COMMIT_NONE
        elif commit_stmt == 'each':
            commit_policy = self.COMMIT_EACH
        elif commit_stmt == 'all':
            commit_policy = self.COMMIT_ALL
        else:
            raise errors.ConfigError('Invalid value for commit_stmt: "{}"'.format(commit_stmt))

        # Substitute params in the DB connection and find it
        db_name = db_name.format(**config)
        db_conn = context.get_db_connection(db_name)

        # Initiate a transaction, if all statements are committed at once
        if not context.dry_run_mode and commit_policy == self.COMMIT_ALL:
            db_conn.begin()

        # Prepare statement(s). If a single statement is given, transform it into a single-element list
        if type(sql) is not list:
            sql = [sql]

        # Prepare parameters, if needed
        db_params = {}
        if params is not None:
            for param in params:
                p_name  = param['name']
                p_value = param['value']
                db_params[p_name] = p_value.format(**config)

        # Execute the statement(s)
        if not context.dry_run_mode:
            for stmt in sql:
                db_conn.execute(stmt, db_params)
                # Commit if needed
                if commit_policy == self.COMMIT_EACH:
                    db_conn.commit()

        # Execute a commit, if all statements are committed at once
        if not context.dry_run_mode and commit_policy == self.COMMIT_ALL:
            db_conn.commit()

        logger.log(context.dry_run_prefix + 'Done. {} statement(s) executed on {}'.format(len(sql), db_name))
