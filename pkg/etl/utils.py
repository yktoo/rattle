"""
Various utility functions
"""
from urllib import request
from urllib.error import HTTPError
import ssl
from .errors import HttpError


def http_fetch(url: str, fail_on_404: bool=True, verify_cert: bool=True, username: str=None, pwd: str='') -> bytes:
    """Fetches and returns data at the specified URL. If server returned an error, an exception is raised.
    :param url: URL to fetch.
    :param fail_on_404: Whether to raise an HTTPError on HTTP 404 error.
    :param verify_cert: Whether to enforce SSL certificate check.
    :param username: Optional username to use for authentication. If None, authentication is not used.
    :param pwd: Optional password to use for authentication. Ignored if username is None.
    :return: Fetched [binary] data as bytes.
    """
    try:
        handlers = []

        # If certificate errors are to be ignored, create a non-verified context
        if not verify_cert:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # Add an HTTPS handler
            handlers.append(request.HTTPSHandler(context=context))

        # If credentials are provided
        if username is not None:
            # Create a password manager
            password_mgr = request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, url, username, pwd)
            # Add a basic authentication handler
            handlers.append(request.HTTPBasicAuthHandler(password_mgr))

        # Create an "opener" (OpenerDirector instance)
        opener = request.build_opener(*handlers)

        # Use the opener to fetch the URL
        response = opener.open(url)

    except HTTPError as e:
        # Special handling of 'File not found' errors
        if e.code == 404:
            if fail_on_404:
                raise HttpError('Failed to fetch {} (file not found)'.format(url))
            return None
        raise

    # If succeeded, read the data and return
    return response.read()
