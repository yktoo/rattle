# line_sorter

`line_sorter` is a [standard handler](index.md) shipped with Rattle. It sorts lines in the input data and returns the result.

## Relevant configuration entries

| Parameter    | Description                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------|
|`input_param` |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_param`|Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`reverse`     |Boolean, whether to reverse-sort lines. Optional, default is `false`.|
