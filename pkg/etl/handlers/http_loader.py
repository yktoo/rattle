from gzip import GzipFile
from io import BytesIO
from etl import logger
from etl import context
from etl import utils
from etl.handlers import base


class Handler(base.Handler):
    """Downloads a file from an HTTP server and returns its contents or, alternatively, downloads several files and runs
    processing on each of them.

    The processing logic is as follows:
    * If the configuration doesn't provide the 'file_defs' array, a single file is downloaded from the URL defined as
      'base_url' and its content is returned via the specified parameter.
    * If 'file_defs' is given, for each file definition:
      - The complete URL of the file is constructed according to the rule.
      - The file is fetched from the HTTP server.
      - The file (i.e. its name and content) is fed to the defined handler script.

    Relevant configuration entries:
        base_url           -- Base URL of the files. Can contain references to configuration parameters in the form
                              '{param_name}'.
        output_param       -- Name of the parameter used for returning result data. Optional, default is 'data'.
        passthrough_params -- Array specifying names of configuration params to be passed-through to child handlers
                              defined by 'file_defs'. Optional. Ignored if 'file_defs' is not specified.
        verify_cert        -- Boolean, if False, SSL certificate validity is not enforced. Optional, default is True.
        detect_compressed  -- Boolean, if True, the downloaded file will be tested for the presence of gzip header, and,
                              if there is one, decompressed. Optional, default is False.
        username           -- Username to use for authentication. Optional, if not specified, no authentication is used.
                              Can contain references to configuration parameters in the form '{param_name}'.
        password           -- Password to use for authentication. Optional, if not specified, empty string is used.
                              Ignored if username is not given. Can contain references to configuration parameters in
                              the form '{param_name}'.
        encoding           -- Encoding to use when decoding the HTTP data. Optional, default is 'utf-8'.
        file_defs          -- Optional array of file definitions. If not given, the page at 'base_url' is fetched and
                              its content is returned via parameter defined in 'output_param'. If given, each entry
                              consists of:
            name      -- Name of the file, relative to 'base_url'. Can contain references to configuration parameters in
                         the form '{param_name}'.
            required  -- Boolean, whether the file is mandatory. If false, no exception will occur on "404" error.
                         Optional, default is True.
            handler   -- Handler configuration (see context.invoke_handler() for details). Handler's configuration will
                         be amended with the elements:
                file_name            -- File name (relative to the base URL).
                <output_param>       -- File contents.
                <passthrough_params> -- All the parameters specified in the 'passthrough_params' list.
    """
    @staticmethod
    def fetch(url: str, required: bool, verify_cert: bool, detect_compressed: bool, username: str, pwd: str, encoding: str) -> str:
        """Fetch a file at the specified URL from the server, decompress if necessary and return its contents.
        :param url: URL to fetch.
        :param required: Whether to raise an exception on HTTP 404 error.
        :param verify_cert: Whether to enforce SSL certificate check.
        :param detect_compressed: Whether to detect and decompress compressed files.
        :param username: Username to use for authentication. If None, authentication is not used.
        :param pwd: Password to use for authentication. Ignored if username is None.
        :param encoding: Encoding to use when decoding the HTTP data.
        :return: File contents as text.
        """
        data = utils.http_fetch(url, required, verify_cert, username, pwd)
        if data is None:
            logger.log('File {} doesn\'t exist')
            return None
        else:
            size_in = len(data)
            logger.log('Downloaded {} ({} bytes)'.format(url, size_in))

            # Check for gzip header if needed, and decompress is it's there
            if detect_compressed and size_in > 10 and data[0] == 0x1F and data[1] == 0x8B:
                compressed_file = BytesIO(data)
                compressed_file.seek(0)
                decompressed_file = GzipFile(fileobj=compressed_file)
                data = decompressed_file.read()
                logger.log('Decompressed the file, raw size is {} bytes'.format(len(data)))

            # Convert the binary data into text
            return data.decode(encoding)

    def run(self, config):
        """Override the abstract method of the base class."""
        # Get attributes from config
        base_url           = config['base_url']
        output_param       = config['output_param',           'data']
        verify_cert        = bool(config['verify_cert',       True])
        detect_compressed  = bool(config['detect_compressed', False])
        file_defs          = config['file_defs',              None]
        passthrough_params = config['passthrough_params',     None]
        username           = config['username',               None]
        password           = config['password',               '']
        encoding           = config['encoding',               'utf-8']

        # Substitute parameter values
        base_url = base_url.format(**config)
        if username is not None:
            username = username.format(**config)
        if password is not None:
            password = password.format(**config)

        # If there are no file definitions
        if file_defs is None:
            # Fetch and return the page at base_url
            return {
                output_param: self.fetch(base_url, True, verify_cert, detect_compressed, username, password, encoding)
            }

        # File definitions present
        else:
            # Prepare child params
            if passthrough_params is None:
                sub_params = {}
            else:
                sub_params = {k: config[k] for k in passthrough_params}

            # Iterate through file definitions
            for file_def in file_defs:
                # Fetch definition details
                fd_name      = file_def['name']
                fd_reqd      = bool(file_def['required', True])
                handler_conf = file_def['handler']

                # Perform config variable substitution
                file_name = fd_name.format(**config)

                # Download file content
                file_content = self.fetch(
                    base_url + file_name, fd_reqd, verify_cert, detect_compressed, username, password, encoding)

                # Run the handler, if the file exists
                if file_content is not None:
                    sub_params['file_name']  = file_name
                    sub_params[output_param] = file_content
                    context.invoke_handler(handler_conf, sub_params)
