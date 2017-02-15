"""
Declares an Bulk DB array inserter class.
"""
from . import connection


class DBArrayInserter(object):
    """Bulk DB array inserter class. Allows for performing massive inserts in the most efficient manner."""

    insert_bind_array_size = 100
    """Number of records inserted at once."""

    def __init__(
            self, db_connection: connection.DBConnection, statement: str, input_sizes: list,
            commit_on_flush: bool=False):
        """Constructor.

        :param db_connection: Connection to use
        :param statement: The insert statement to use
        :param input_sizes: List specifying data types of the inserted data
        :param commit_on_flush: Whether to commit the changes on each flush
        """
        self._connection      = db_connection
        self._statement       = statement
        self._commit_on_flush = commit_on_flush
        # Create and set up a cursor
        self._cursor = self._connection.cursor(array_bind_size=self.insert_bind_array_size, input_sizes=input_sizes)
        self._row_data = []

    def __del__(self):
        """Destructor. Destroys the insert statement."""
        self._cursor.close()

    def flush(self):
        """Executes the insert statement with all the available row data, and commits the result."""
        if len(self._row_data) > 0:
            self._cursor.executemany(self._statement, self._row_data)
            if self._commit_on_flush:
                self._connection.commit()
            # Free the data
            self._row_data = []

    def push_row(self, row: [tuple, list]):
        """Pushes another row to be inserted.

        :param row Tuple of values for insert.
        """
        self._row_data.append(row)
        # Flush the data as soon as we've hit the array size limit
        if len(self._row_data) == self.insert_bind_array_size:
            self.flush()
