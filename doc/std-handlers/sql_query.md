# sql_query

`sql_query` is a [standard handler](index.md) shipped with Rattle. It allows to execute an SQL query and fetch data from a database.

## Relevant configuration entries

| Parameter        | Description                                                                                       |
|------------------|---------------------------------------------------------------------------------------------------|
|`output_param`    |Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`database`        |Name of the target database connection.|
|`field_delimiter` |String to be used as field delimiter in the output text. Optional, default is empty string.|
|`record_delimiter`|String to be used as record delimiter in the output text. Optional, default is the new line character.|
|`col_headers`     |Boolean, if `true`, outputs column headers as the first record, separated by `field_delimiter` and quoted by `quotechar`. Optional, default is `false`.|
|`quotechar`       |Quote character or string for field values and column names. Optional, if specified, the following rules apply:<br>• `"("` causes the value to be enclosed in brackets `()`.<br>• `"["` causes the value to be enclosed in square brackets `[]`.<br>• `"{"` causes the value to be enclosed in curly braces `{}`.<br>• Any other string is used for enclosing the value as is.|
|`sql`             |SQL query. May contain external parameter references (not to be confused with handler configuration parameters) in the form appropriate for the database in use. For example, Oracle uses colon-prefixed notation, such as `":name"`. In this case, `:name` must also be defined in the `params` configuration parameter (see below).|
|`params`          |Array of parameter definitions. Optional if no parameter references are used in `sql`. Each element is an object consisting of:|
|•  `name`         |Parameter name.|
|•  `value`        |Parameter value. Can refer to handler configuration parameters in the form `"{param_name}"`.|
