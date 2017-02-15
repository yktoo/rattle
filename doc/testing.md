# Unit tests

Rattle uses the [nose](https://nose.readthedocs.org/) Python library as a test runner (refer to the [Requirements](requirements.md) page for version details).

In order to run the tests:

1. Make sure `nose` is installed.
2. Navigate to the root of the project source tree (containing the `pkg` directory).
3. Run the command:
```bash
nosetests3 [-v] [-s] pkg/
```

This will run *all* unit tests available. You can use the following additional options:
* `-v` - be more verbose (list individual tests).
* `-s` - do not capture stdout (can be helpful to identify the cause of the failure).
