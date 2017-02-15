# xslt

`xslt` is a [standard handler](index.md) shipped with Rattle. It applies an [XSLT transformation](http://www.w3schools.com/xsl/) to the input XML data, and returns the result.

## Relevant configuration entries

| Parameter     | Description                                                                                          |
|---------------|------------------------------------------------------------------------------------------------------|
|`input_param`  |Name of the parameter used for reading input data. Optional, default is `"data"`.|
|`xslt_param`   |Name of the parameter used for reading XSLT data. Optional, default is `"xslt"`.|
|`output_param` |Name of the parameter used for returning result data. Optional, default is `"data"`.|
|`pretty_output`|Boolean, whether to represent the output as formatted XML. Optional, default is `false`.|

## Remarks

1. Both input data (provided via `input_param`) and XSLT data (provided via `xslt_param`) must represent *valid XML*, otherwise an error will be raised.
2. This handler is also capable of producing plain-text output. In order to do that, define the `method` attribute of `xsl:output` element as follows:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" omit-xml-declaration="yes" media-type="string"/>
    ...
</xsl:stylesheet>
```
