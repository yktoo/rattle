# dir_lister

`dir_lister` is a [standard handler](index.md) shipped with Rattle. It lists the contents of a directory according to specified mask(s) and returns it as list of file/directory names.

## Relevant configuration entries

| Parameter       | Description                                                                                        |
|-----------------|----------------------------------------------------------------------------------------------------|
|`file_masks`     |Full path to the directory, including file name mask, e.g. `"/tmp/*.txt"`, or an array of such paths. Can contain references to configuration parameters in the form `"{param_name}"`. If the mask is not absolute, it's considered to be relative to the current configuration file's path.|
|`include_files`  |Boolean. Whether to include files. Optional, default is `true`.|
|`include_dirs`   |Boolean. Whether to include directories. Optional, default is `true`.|
|`output_param`   |Name of the parameter used for returning result data. Optional, default is `"data"`.|

**NB:** This handler will issue a warning if both `include_files` and `include_dirs` are `false`, since the output will always be empty.
