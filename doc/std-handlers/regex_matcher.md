# regex_matcher

`regex_matcher` is a [standard handler](index.md) shipped with Rattle. It captures matches in the input data based on regex patterns and returns them as lines.

## Relevant configuration entries

| Parameter    | Description                                                                                           |
|--------------|-------------------------------------------------------------------------------------------------------|
|`input_param` |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`output_param`|Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`regex`       |Regular expression to run against the data.|
|`group_num`   |Number of capture group containing the result of the match (`0` for the whole match, `1` for the first captured expression and so on).|
|`unique`      |Boolean, specifies where the list of matches has to be deduplicated before handler invocation. Optional, default is `false`.|

**NB:** The matches (represented as lines, separated by line-breaks) in the output data will follow the same order as in the input data.

## Example

The snippet below will find and return all unique digit occurrences in the input data. Notice the use of `\\` , which is required to escape the slash character in JSON.

```json
{
    "module": "regex_matcher",
    "regex": "(\\d+)",
    "group_num": 1,
    "unique": true
}
```
