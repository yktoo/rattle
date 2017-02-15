# file_reader

`file_reader` is a [standard handler](index.md) shipped with Rattle. It reads in a text file and returns its contents.

## Relevant configuration entries

| Parameter       | Description                                                                                        |
|-----------------|----------------------------------------------------------------------------------------------------|
|`file_name`      |Full path to the input file. Can contain references to configuration parameters in the form `"{param_name}"`. If it's not absolute, it's considered to be relative to the current configuration file's path.|
|`output_param`   |Name of the parameter used for returning result data. Optional, default is `"data"`.|

**NB:** This handler will raise an error if the specified file doesn't exist.
