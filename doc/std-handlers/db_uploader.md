# db_uploader

`db_uploader` is a [standard handler](index.md) shipped with Rattle. It allows to upload tabular data, either fixed-width or delimited, to a database table.

Input records must be separated by the newline character.

## Relevant configuration entries

| Parameter       | Description                                                                                        |
|-----------------|----------------------------------------------------------------------------------------------------|
|`input_param`    |Name of the parameter used for reading input data. Optional, default is `data`.|
|`format`         |Format of the input data, either `fixed` (fixed-width fields) or `delimited` (fields are delimited with `delimiter`).|
|`delimiter`      |Field delimiter character. Mandatory if `format` is `delimited`, otherwise ignored.|
|`quotechar`      |Quote character. Optional if `format` is `delimited`, otherwise ignored.|
|`start_line`     |Integer, number of the line to start data import with (1-based). Optional, default is `1`.|
|`target_database`|Name of the target database connection.|
|`target_table`   |Name of the target table, possibly with schema name before it.|
|`truncate_target`|Boolean, whether or not to truncate the target table before the load. Optional, `false` by default.|
|`column_mappings`|Array of objects describing column mappings, each object consisting of:|
|• `name`         |(Display) name of the column.|
|• `datatype`     |Datatype of the column, one of `string`, `number`, `integer`, `datetime`. Mandatory if `source_pos`/`source_index` is specified.|
|• `length`       |Data length, integer in the range 1..4000. Mandatory for columns of datatype `string`, ignored for all other datatypes.|
|• `truncate`     |Whether to truncate data whose length exceeds length value. When such a value is encountered, if truncate is `true`, it gets shortened to the value of `length`; if truncate is `false`, in error is raised and processing fails. Optional for columns of datatype `string`, ignored for all other datatypes. |
|• `source_pos`   |Column boundary specification in the format `"<left_pos>:<right_pos>"`, where `<left_pos>` and `<right_pos>` are 1-based column left and right boundaries, respectively. For example, in the string `"abc defg"` column 1 has boundaries `"1:3"` and column 2 boundaries `"5:8"`.<br>• **Fixed-width files:** optional, if omitted, `target_expr` must represent a constant expression or a built-in database function.<br>• **Delimited files:** ignored.|
|• `source_index` |0-based index of the source column in the data:<br>• **Fixed-width files:** ignored.<br>• **Delimited files:** optional, if omitted, `target_expr` must represent a constant expression or a built-in database function.|
|• `source_trim`  |Trimming (whitespace removal) mode for source values, one of:<br>• `none` - no trimming will occur;<br>• `left` - trim leading whitespace;<br>• `right` - trim trailing whitespace;<br>• `both` - trim leading and trailing whitespace.<br><br>Optional, default is `none`.|
|• `source_format`|Optional, format for source data for the datetime datatype.|
|• `target_column`|Name of the column in the `target_table`.|
|• `target_expr`  |Expression to use for the inserted value. The following rules apply:<br>• If the source value (`source_pos`/`source_index`) is provided, `target_expr` is optional, and, if given, it can refer to the source value as `"{value}"`. If omitted, the source value us used as-is.<br>• If no source value is provided, `target_expr` is mandatory, and it can refer to the current target row number (1-based) as `"{rownum}"`.<br><br>In both cases it can additionally refer to config parameters in the form `"{param_name}"`.|
