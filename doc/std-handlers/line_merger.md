# line_merger

`line_merger` is a [standard handler](index.md) shipped with Rattle. It merges every `N` lines of the input data into one, with an optional delimiter, and returns the result.

## Relevant configuration entries

| Parameter          | Description                                                                                     |
|--------------------|-------------------------------------------------------------------------------------------------|
|`input_param`       |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_param`      |Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`start_line`        |Integer, number of the line to start data import with (1-based). Optional, default is `1`.|
|`num_lines_to_merge`|Number of lines to concatenate into one.|
|`trim_lines`        |Boolean, whether to trim (remove all leading and trailing whitespace from) the lines being merged. Optional, default is `false`.|
|`skip_blank_lines`  |Boolean, whether to skip blank lines (if `true`, blank lines are not counted for merging). Optional, default is `false`.<br>**NB:** detection of blank lines is influenced by the value of `trim_lines`.|
|`delimiter`         |Delimiter string to insert between concatenated strings. Optional, default is `""` (an empty string).|
