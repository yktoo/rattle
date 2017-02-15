# http_loader

`http_loader` is a [standard handler](index.md) shipped with Rattle. It downloads a file from an HTTP server and returns its contents or, alternatively, downloads several files and runs processing on each of them.

The processing logic is as follows:

* If the configuration doesn't provide the `file_defs` array (*"simple" mode*):
    1. A single file is downloaded from the URL defined as `base_url`
    2. If detect_compressed is `true`, the file is checked for the presence of gzip header, and, if there is one, the content gets decompressed.
    3. File content is returned via the specified parameter.
* If `file_defs` **is** given, for each file definition:
    1. The complete URL of the file is constructed according to the rule.
    2. The file is fetched from the HTTP server.
    3. If `detect_compressed` is `true`, the file is checked for the presence of gzip header, and, if there is one, the content gets decompressed.
    4. The file (i.e. its name and content) is fed to the defined `handler`.

## Relevant configuration entries

| Parameter         | Description                                                                                      |
|-------------------|--------------------------------------------------------------------------------------------------|
|`base_url`         |Base URL of the files. Can contain references to configuration parameters in the form `"{param_name}"`.|
|`output_param`     |Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`passthrough_param`|Array specifying names of configuration parameters to be passed-through to child handlers defined by `file_defs`. Optional. Ignored if `file_defs` is not specified.|
|`verify_cert`      |Boolean, if `false`, SSL certificate validity is not enforced. Optional, default is `false`.|
|`detect_compressed`|Boolean, if `true`, the downloaded file will be tested for the presence of gzip header, and, if there is one, decompressed. This setting affects both "simple" and `file_defs` mode. Optional, default is `false`.|
|`username`         |Username to use for authentication. Optional, if not specified, no authentication is used. Can contain references to configuration parameters in the form `"{param_name}"`.|
|`password`         |Password to use for authentication. Optional, if not specified, empty string is used. Ignored if `username` is not given. Can contain references to configuration parameters in the form `"{param_name}"`.|
|`encoding`         |Encoding to use when decoding the HTTP data. Optional, default is `utf-8`. See [Python codec documentation](https://docs.python.org/3.4/library/codecs.html#standard-encodings) for the complete encoding list.|
|`file_defs`        |Optional array of file definitions. If not given, the page at `base_url` is fetched and its content is returned via parameter defined as `output_param`.<br>If given, each entry consists of:|
|• `name`           |Name of the file, relative to `base_url`. Can contain references to configuration parameters in the form `"{param_name}"`.|
|• `required`       |Boolean, whether the file is mandatory. If `false`, no exception will occur on "404" error. Optional, default is `true`.|
|• `handler`        |Handler configuration, which will be amended with the following elements:|
|&nbsp;&nbsp;&nbsp; • `file_name`           |File name (relative to the `base_url`).|
|&nbsp;&nbsp;&nbsp; • `<output_param>`      |File contents.|
|&nbsp;&nbsp;&nbsp; • `<passthrough_params>`|All the parameters specified in the `passthrough_params` list.|

**NB:** This handler will raise an error if it failed to download any of the specified files; the only exception is "HTTP 404 Not Found" errors for file
definitions with `required=false`, in which case no error is raised and no handler is invoked.
