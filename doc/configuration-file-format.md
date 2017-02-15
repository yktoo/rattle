# Configuration file format

Rattle uses (a hierarchy of) configuration files in the [JSON](http://www.json.org/) format. This format is flexible enough to be able to describe a wide range of configurations; it is possible to decompose big files that threaten to grow out of control into smaller, better manageable chunks, and include the latter from the former.

## Configuration file contents

At its top level, this file contains the following objects:

| Key name         | Type  | Mandatory | Description                                                                   |
|------------------|-------|-----------|-------------------------------------------------------------------------------|
|`processes`       |Array  |    Yes    |Array of objects, each defining a certain *data integration process*, by providing the following elements:|
|• `name`          |String |    Yes    |Name of the process.|
|• `comment`       |String |    No     |Description of the process. Default is empty string.|
|• `stop_on_error` |Boolean|    No     |Whether to terminate processing on an unhandled exception. Default is `true`.|
|• `handler`       |Handler|    Yes    |[Handler configuration](handler-configuration.md).|
|`databases`       |Array  |    No*    |* Mandatory if any handlers requiring a database connection are used.<br>Database configuration. Each element is an object describing a database connection by providing the following elements:|
|`name`            |String |    Yes    |Unique database name, used as a reference in other places.|
|`connection`      |String |    Yes    |Database connection string in the following format:<br>`driver_name:driver_specific_connection_string`<br><br>The following drivers are currently available:<br>• Database: Oracle. Driver name: `oracle`. Connection string format: `oracle:<host>:<port>:<sid>`. Requirements: cx_Oracle 5.1.3+.|
|`username`        |String |    Yes    |DB user name.|
|`password`        |String |    Yes    |DB user password.<br>The password can be given either in plain text or as a Base64-encoded string; in the latter case it must be prefixed with " BASE64:" , for example:<br>`{`<br>`    "name": "main",`<br>`    "connection": "Secret",`<br>`    "username": "Facility",`<br>`    "password": "BASE64:VG9wU2VjcmV0"`<br>`}`<br><br>To encode a password use the command:<br>`echo -n 'MyPassword' | base64`<br>And to decode a password the command:<br>`echo -n 'TXlQYXNzd29yZA==' | base64 -d`|
|`file_name`       |String |    No     |Optional path to the external file that contains DB connection parameters in an object that provides any of the following keys:<br>• `connection`<br>• `username`<br>• `password`<br>This path can be either *absolute* or *relative to the location of the current configuration file*. It can also include globals defined either in the `globals` object (see below) or via the `-g` command-line option, for example: `"/path/to/{MY_PARAM}.json"`.<br>Values given in this file override same-named values specified in the main DB connection configuration, which allows to store connection parameters, such as passwords, in an external (environment-specific) file.|
|`log`             |Object |    No     |Logging configuration, consisting of the following elements:|
|`file`            |String |    No     |Name of the log file. If omitted, all the logging will be output to the standard output (`stdout`) for messages with severities **DEBUG** and **INFO**, and to the standard error (`stderr`) for messages with severities **WARNING** and **ERROR**.|
|`verbose`         |Boolean|    No     |Whether verbose logging must be used. In non-verbose mode messages with **DEBUG** severity are not logged. Default is `false`.<br>**Note:** this setting can be overridden on the command line with the `--verbose` / `--no-verbose` options.|
|`globals`         |Object |    No     |Object defining global configuration parameters that will be passed to every handler (but can be overridden by scoped parameters or using the `-g` command line option, see [Synopsis](index.md)).|

## See also

* [Handler configuration](handler-configuration.md)
* [Configuration examples](configuration-examples.md)
