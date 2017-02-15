"""
Declares a unified database connection class.
"""
import abc
from importlib import import_module

# Static map of driver names to their modules
DRIVER_MAP = {
    'oracle': 'etl.db.drivers.oracle'
}


class DatabaseError(Exception):
    """Errors raised by database related objects."""
    pass


class BaseDriver(object, metaclass=abc.ABCMeta):
    """Abstract base class for database drivers."""

    def __init__(self, connect_string: str, username: str, password: str):
        """Constructor.
        :param connect_string Driver-dependent string describing connection parameters
        :param username DB user name
        :param password DB password
        """
        self.connect_string = connect_string
        self.username       = username
        self.password       = password
        # Establish connection
        self.connect()

    def __del__(self):
        """Destructor."""
        self.disconnect()

    @abc.abstractmethod
    def connect(self):
        """Connect to the DB."""

    @abc.abstractmethod
    def disconnect(self):
        """Disconnect from the DB."""

    @abc.abstractmethod
    def begin(self):
        """Explicitly begin a new transaction in the database."""

    @abc.abstractmethod
    def commit(self):
        """Commit any pending transactions to the database."""

    @abc.abstractmethod
    def cursor(self, array_bind_size: int, input_sizes: list):
        """Create and return a new cursor object. The created cursor must be closed after use.
        :param array_bind_size: Size of the array bind buffer, in rows, for the sake of efficiency. Optional.
        :param input_sizes: List of sizes of input parameters, for the sake of efficiency. Optional.
        """

    @abc.abstractmethod
    def datatype_map(self):
        """Return dictionary mapping five base types to respective values."""

    @abc.abstractmethod
    def get_datetime_expression(self, value, fmt):
        """Return a string to be used as a parameter placeholder for positional binding.
        :param value: String (expression) to be converted into datetime.
        :param fmt: Format expression the value is in.
        """

    @abc.abstractmethod
    def get_param_placeholder(self, param_id):
        """Return a string to be used as a parameter placeholder for positional binding.
        :param param_id: Unique parameter identifier.
        """

    @abc.abstractmethod
    def rollback(self):
        """Rolls back any pending transactions in the database."""

    @abc.abstractmethod
    def version(self):
        """Returns the version of the database."""


class DBConnection():
    """Unified database connection class."""

    # Standard data types
    BINARY   = None
    DATETIME = None
    NUMBER   = None
    ROWID    = None
    STRING   = None

    def __init__(self, connect_string: str, username: str, password: str):
        """Constructor.
        :param connect_string String describing connection parameters in the format:
            '<driver_name>:<driver_specific_configuration>'
        :param username DB user name
        :param password DB password
        """
        # Parse the connection string
        conn = connect_string.partition(':')
        if conn[0] == '':
            raise DatabaseError('Invalid connection string: driver name not found.')
        if conn[1] != ':':
            raise DatabaseError('Invalid connection string: separator (:) not found.')
        if conn[2] == '':
            raise DatabaseError('Invalid connection string: driver configuration not found.')
        self.driver_name = conn[0]
        self.driver_conf = conn[2]

        # Identify the required driver
        if self.driver_name not in DRIVER_MAP:
            raise DatabaseError('No known driver available for "{}"'.format(self.driver_name))
        self.driver_module_name = DRIVER_MAP[self.driver_name]

        # Import the corresponding handler module
        driver_module = import_module(self.driver_module_name)

        # Find driver class object
        driver_class = getattr(driver_module, 'Driver')
        assert issubclass(driver_class, BaseDriver)

        # Create a driver
        self._driver = driver_class(self.driver_conf, username, password)

        # Initialise data types
        dtmap = self._driver.datatype_map()
        self.BINARY   = dtmap['BINARY']
        self.DATETIME = dtmap['DATETIME']
        self.NUMBER   = dtmap['NUMBER']
        self.ROWID    = dtmap['ROWID']
        self.STRING   = dtmap['STRING']

    def begin(self):
        """Explicitly begin a new transaction in the database."""
        self._driver.begin()

    def commit(self):
        """Commit any pending transactions to the database."""
        self._driver.commit()

    def cursor(self, array_bind_size: int=None, input_sizes: list=None):
        """Create and return a new cursor object. The created cursor must be closed after use."""
        return self._driver.cursor(array_bind_size, input_sizes)

    def get_datetime_expression(self, value, fmt):
        """Return a string to be used as a parameter placeholder for positional binding.
        :param value: String (expression) to be converted into datetime.
        :param fmt: Format expression the value is in.
        """
        return self._driver.get_datetime_expression(value, fmt)

    def get_param_placeholder(self, param_id):
        """Return a string to be used as a parameter placeholder for positional binding.
        :param param_id: Unique parameter identifier
        """
        return self._driver.get_param_placeholder(param_id)

    def execute(self, sql: str, params: dict=None):
        """Executes an SQL command against the database."""
        cur = self.cursor()
        cur.execute(sql, params if params is not None else [])
        cur.close()

    def query_value(self, sql: str, params: dict=None):
        """Returns a single value as a result of an SQL query."""
        cur = self.cursor()
        cur.execute(sql, params if params is not None else [])
        v = cur.fetchone()[0]
        cur.close()
        return v

    def rollback(self):
        """Rolls back any pending transactions in the database."""
        self._driver.rollback()

    def version(self):
        """Returns the version of the database."""
        return self._driver.version
