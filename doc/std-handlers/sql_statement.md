# sql_statement

`sql_statement` is a [standard handler](index.md) shipped with Rattle. It allows to execute one or more SQL statements against the database.

## Relevant configuration entries

| Parameter   | Description                                                                                            |
|-------------|--------------------------------------------------------------------------------------------------------|
|`database`   |Name of the target database connection.|
|`sql`        |SQL statement or an array of SQL statements to execute.<br>Statements may contain external parameter references (not to be confused with handler configuration parameters) in the form appropriate for the database in use. For example, Oracle uses colon-prefixed notation, such as `":name"`. In this case, `:name` must also be defined in the `params` configuration parameter (see below).|
|`commit_stmt`|Statement commit policy. Allowed values are:<br>• `"none"` - Do not issue any implicit commits.<br>• `"each"` - Commit after each statement.<br>• `"all"` - Commit once after all statements.<br><br>Optional, default is `"each"`.|
|`params`     |Array of parameter definitions. Optional if no parameter references are used in `sql`. Each element is an object consisting of:|
|• `name`     |Parameter name.|
|• `value`    |Parameter value. Can refer to handler configuration parameters in the form `"{param_name}"`.|
