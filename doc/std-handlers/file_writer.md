# file_writer

`file_writer` is a [standard handler](index.md) shipped with Rattle. It writes the provided input data into a file. This is also often useful for debugging.

## Relevant configuration entries

| Parameter       | Description                                                                                        |
|-----------------|----------------------------------------------------------------------------------------------------|
|`input_param`    |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_file`    |Path to the output file. Can contain references to configuration parameters in the form `"{param_name}"`. If it's not absolute, it's considered to be relative to the current configuration file's path.|
|`append`         |Boolean, whether to overwrite (`false`) or append (`true`) the file if it exists. Optional, default is `false`.|

**NB:** This handler will raise an error if it failed to open the specified file for writing.
