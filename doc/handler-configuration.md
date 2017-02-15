# Handler configuration

A special type of [ETL configuration](configuration-file-format.md) entry, `handler`, is used to describe a *parameter block*, a single *handler block* or a list of them. Thus, handler configuration refers to one of the following options:

* A **parameter block**, which is an object describing an arbitrary number of parameters. These parameters will be *published* on the pipeline, for example:
    ```json
    {
        "a": 10,
        "b": "my_file.txt"
    }
    ```
    In this scenario parameters `a` and `b` will be present down on the pipeline after the above block is executed.<br>
    **NB:** a parameter block cannot set the value of the `module` parameter, because it would turn it into a handler block (see below).

* A **handler block**, i.e. an object describing a handler by providing the following elements:

| Key name | Type | Mandatory | Description |
|----------|------|-----------|-------------|
|`module`  |String|    Yes    |Python module containing handler code. Can be either a fully qualified name that includes package name, or a simple name that is considered one of the [standard library handlers](std-handlers/index.md) (i.e. the `etl.handlers` package).|
|`class`   |String|    No     |Handler class to instantiate. Optional, the default is `Handler`.|
|`comment` |String|    No     |Additional info about the step the handler executes. Can contain references to other configuration parameters in the form `"{param_name}"`.|
|          |      |           |*(any other handler-specific parameters)*|

* An **array** of parameter or handler blocks described above, to *chain* blocks. An array implicitly creates a so-called *pipeline*, which shares everything produced by parameter or handler blocks inside it. It is also possible to nest arrays of objects; all of these nested pipelines will share the same parameters.

* A **string** specifying the path to an *include-file* in JSON format. This path can be either *absolute* or *relative to the location of the current file*. The content of the included file will be used instead of the provided path value, so the file must contain one of the objects mentioned above.
