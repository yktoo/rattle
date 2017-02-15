# Standard handlers

All the functionality in the Rattle application is realised by *handlers*, small building blocks written in Python and interacting with the application via
a standardised interface.

The application is shipped with a number of standard, generic handlers, all belonging to the `etl.handlers` Python package. Since this is the default handler package for Rattle, you don't need to explicitly specify it in the module parameter value of the [configuration file](../configuration-file-format.md), e.g. `http_loader` instead of `etl.handlers.http_loader` (though the latter version is also valid).

At the moment the following standard handlers are available:

|Module                           | Description |
|---------------------------------|-------------|
|[db_uploader](db_uploader.md)    |Allows to upload tabular data, either fixed-width or delimited, to a database table. Input records must be separated by a newline character.|
|[dir_lister](dir_lister.md)      |Lists the contents of a directory and returns it as list of file/directory names.|
|[file_reader](file_reader.md)    |Reads in a text file and returns its contents.|
|[file_writer](file_writer.md)    |Writes provided data into a file.|
|[http_loader](http_loader.md)    |Downloads a file from an HTTP server and returns its contents or, alternatively, downloads several files and runs processing on each of them.|
|[line_filter](line_filter.md)    |Filters lines in the input data based on the specified criteria and returns the result.|
|[line_iterator](line_iterator.md)|Iterates through lines in the data and invokes a handler on each of them.|
|[line_merger](line_merger.md)    |Merges every N lines of the input data into one, with an optional delimiter, and returns the result.|
|[line_sorter](line_sorter.md)    |Sorts lines in the input data and returns the result.|
|[regex_matcher](regex_matcher.md)|Captures matches in the input data based on regex patterns and returns them as lines of text.|
|[sql_query](sql_query.md)        |Allows to execute an SQL query and fetch data from a database.|
|[sql_statement](sql_statement.md)|Allows to execute one or more SQL statements against a database.|
|[str_replacer](str_replacer.md)  |Replaces occurrences of substrings or regex patterns in the input data and returns the result.|
|[xslt](xslt.md)                  |Applies XSLT transformation to input XML data, and returns the result.|
