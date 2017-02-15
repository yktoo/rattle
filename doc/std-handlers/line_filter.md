# line_filter

`line_filter` is a [standard handler](index.md) shipped with Rattle. It filters lines in the input data based on the specified criteria and returns the result.

## Relevant configuration entries

| Parameter           | Description                                                                                    |
|---------------------|------------------------------------------------------------------------------------------------|
|`input_param`        |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_param`       |Name of the parameter used for returning lines that pass the filter. Optional, default is `"data"`.|
|`rejected_param`     |Name of the parameter used for returning lines that don't pass the filter. Optional, if not specified, the rejected lines are discarded.|
|`start_line`         |Integer, number of the line to start data reading with (1-based). Optional, default is `1`.<br>**NB:** counting for the start line ignores the `skip_blank_lines` setting.|
|`skip_blank_lines`   |Boolean. Whether to skip blank lines. Optional, default is `false`.|
|`criteria`           |A filtering criterion or an array of such criteria. Optional. If specified, only those input lines that match all criteria are added to the output set. Each criterion is an object with the following elements:|
|• `search`           |Substring or regex pattern to match against each input line.|
|• `is_regex`         |Boolean. Whether search is a substring (`false`) or a regular expression (`true`) to match. Optional, default is `false`.|
|• `substitute_params`|Boolean. Whether search should be searched for parameter substitutions in the form `"{param_name}"`, whose occurrences will be replaced with the respective parameter values. Optional, default is `false`.|
|• `negate`           |Boolean. Whether lines matching this rule are to be included in (`false`) or excluded (`true`) from the output set. Optional, default is `false`.|
