# str_replacer

`str_replacer` is a [standard handler](index.md) shipped with Rattle. It replaces occurrences of substrings or regex patterns in the input data and returns the result.

## Relevant configuration entries

| Parameter    | Description                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------|
|`input_param` |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_param`|Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`rules`       |Array of entries describing replacement rules. Each entry is an object with the following elements:|
|• `search`    |Substring or pattern to search.|
|• `replace`   |Substring to replace whatever is found for `search`.|
|• `count`     |Maximal number of occurrences to replace. If `0`, all occurrences are replaced. Optional, default is `0`.|
|• `is_regex`  |Boolean. Whether search is a substring (`false`) or a regular expression (`true`) to match. Optional, default is `false`.|
