# Installation

The Rattle application can be installed in the following two ways.

## Deployment mode

This is the **standard way** of installing the tool, suitable for e.g. production deployment. It uses a distribution tarball and requires `root` or administrator privileges on the target system.

To install the application:

1. Copy the `rattle-X.X.X.tar.gz` tarball to the target machine.
2. `tar xf rattle-X.X.X.tar.gz`
3. `cd rattle-X.X.X`
4. `sudo python3 setup.py install`

## Development mode

If the application is installed in **development mode**, it does not require reinstalling when the source code changes. It is achieved by creating links to packages instead of copying files.

To install the application in development mode:

1. Clone the [source code repository](https://github.com/yktoo/rattle) or otherwise copy the source code tree.
2. Navigate to the root directory of the project containing `setup.py`.
3. Run:
    a. To install the application system-wide:
    ```bash
    sudo python3 setup.py develop
    ```
    b. To install the application for the current user only:
    ```bash
    python3 setup.py develop --user
    ```

## See also

* [Requirements](requirements.md)
