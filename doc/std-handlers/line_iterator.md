# line_iterator

`line_iterator` is a [standard handler](index.md) shipped with Rattle. It iterates through the lines in the input data and invokes a handler on each of them,
thus providing some kind of "loop" functionality.

## Relevant configuration entries

| Parameter              | Description                                                                                 |
|------------------------|---------------------------------------------------------------------------------------------|
|`input_param`           |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_param`          |Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`passthrough_params`    |Array specifying names of configuration parameters to be passed-through to child handlers. Optional.|
|`chomp`                 |Boolean, whether to strip the terminating line-break. Optional, default is `true`.|
|`skip_blank_lines`      |Boolean, whether to skip invoking handler for blank lines (**NB:** this is also influenced by the value of `chomp`). Optional, default is `true` .|
|`handler`               |Handler configuration, which will be amended with the following elements:|
|• `<output_param>`      |One current line from the source data.|
|• `<passthrough_params>`|All the parameters specified in the `passthrough_params` list.|
