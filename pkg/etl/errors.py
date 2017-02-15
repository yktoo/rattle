"""
Exception class declarations.
"""


class EtlError(Exception):
    """Base class for all ETL-related exceptions."""
    pass


class LogicError(EtlError):
    """Exception raised for errors related to the execution logic."""
    pass


class ConfigError(EtlError):
    """Exception raised for configuration-related errors."""
    pass


class FileError(EtlError):
    """Exception raised for file-related errors."""
    pass


class HttpError(EtlError):
    """Exception raised for HTTP-related errors."""
    pass


class DatabaseError(EtlError):
    """Exception raised for database-related errors."""
    pass


class DataError(EtlError):
    """Exception raised for data-related errors."""
    pass
