"""
Oracle driver implementation.

Dependencies / Configuration Notes
==================================
The whole setup was tested on 64-bit Linux and Windows.

- Python 3.4 64-bit
- Oracle Instant Client 11.2 64-bit
- cx_Oracle 5.1.3 py27-x86_64 [ http://cx-oracle.sourceforge.net/ ]

Oracle Instant Client configuration
-----------------------------------
1. The library path has to be present in the PATH env variable, e.g. C:\Oracle\instantclient_11_2_64bit
2. Add an env variable ORACLE_HOME=C:\Oracle\instantclient_11_2_64bit
"""

import cx_Oracle
from etl.db.connection import BaseDriver, DatabaseError


class Driver(BaseDriver):
    """Oracle driver implementation."""

    def __init__(self, connect_string: str, username: str, password: str):
        self._connection = None
        super().__init__(connect_string, username, password)

    def connect(self):
        # Parse and check connection string
        params = self.connect_string.split(':')
        if len(params) != 3:
            raise DatabaseError('Oracle driver specification must be in format "host:port:sid"')
        # Create a new connection
        self._connection = cx_Oracle.connect(
            self.username, self.password, cx_Oracle.makedsn(params[0], int(params[1]), params[2]))

    def disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def begin(self):
        self._connection.begin()

    def commit(self):
        self._connection.commit()

    def cursor(self, array_bind_size: int, input_sizes: list):
        cur = self._connection.cursor()
        if array_bind_size is not None:
            cur.bindarraysize = array_bind_size
        if input_sizes is not None:
            cur.setinputsizes(*input_sizes)
        return cur

    def datatype_map(self) -> dict:
        return {
            'BINARY':   cx_Oracle.BINARY,
            'DATETIME': cx_Oracle.DATETIME,
            'NUMBER':   cx_Oracle.NUMBER,
            'ROWID':    cx_Oracle.ROWID,
            'STRING':   cx_Oracle.STRING,
        }

    def get_datetime_expression(self, value, fmt):
        return "To_Date({}, {})".format(value, fmt)

    def get_param_placeholder(self, param_id):
        return ':{}'.format(param_id)

    def rollback(self):
        self._connection.rollback()

    def version(self) -> str:
        return self._connection.version
