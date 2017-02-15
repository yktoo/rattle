# Rattle

## Abstract

**Rattle** is a flexible data integration or ETL (**E**xtract, **T**ransform, **L**oad) program. What it does, is completely defined by the configuration file whose name is passed on the command line.

## Synopsis

```bash
rattle [-h] [-n] [-v] [-V] [-g NAME=VALUE] config_file
```

where:

* `-h, --help`<br>
  Show program usage help and exit
* `-n, --dry-run`<br>
  Do not make any changes to the database
* `-v, --verbose`<br>
  Force use of verbose logging, overrides configuration file setting, takes precedence over -V
* `-V, --no-verbose`<br>
  Force use of non-verbose logging, overrides configuration file setting
* `-g NAME = VALUE , --add-global NAME = VALUE`<br>
  Register a global parameter named NAME having value VALUE . Overrides same-named parameter in the GLOBALS section of the configuration file, if any. This option can be used to register multiple parameters, in which case it has to be repeated the required number of times.
* `config_file`<br>
  Path to a JSON [configuration file](configuration-file-format.md).

## Description

The key parameter that must be supplied to the application is a configuration file, please refer to the [Configuration file format](configuration-file-format.md) page for details and the [Configuration examples](configuration-examples.md) page.

The application is shipped with a number of [standard handlers](std-handlers/index.md) capable of executing basic ETL operations.

## Requirements

Refer to the [Requirements](requirements.md) document.

## Installation

Refer to the [Installation](installation.md) document.

## Testing

Refer to the [Testing](testing.md) document.

## Bundling

To create a distribution package, run:

```bash
python3 setup.py sdist
```

## License

[MIT](https://opensource.org/licenses/MIT)
