import lxml.etree
from etl import logger
from etl.handlers import base


class Handler(base.Handler):
    """Applies XSLT transformation to input XML data, and returns the result.

    Relevant configuration entries:
        input_param    -- Name of the parameter used for reading input data. Optional, default is 'data'.
        xslt_param     -- Name of the parameter used for reading XSLT data. Optional, default is 'xslt'.
        output_param   -- Name of the parameter used for returning result data. Optional, default is 'data'.
        pretty_output  -- Boolean, whether to represent the output as formatted XML. Optional, default is False.

    :return dict containing parameter whose name is given by 'output_param'.
    """
    def run(self, config) -> dict:
        """Override the abstract method of the base class."""
        # Get attributes from config
        input_param   = config['input_param',  'data']
        xslt_param    = config['xslt_param',   'xslt']
        output_param  = config['output_param', 'data']
        pretty_output = config['pretty_output', False]

        # Read and parse the input and XSLT data
        data_dom = lxml.etree.fromstring(config[input_param].encode())
        xslt_dom = lxml.etree.fromstring(config[xslt_param].encode())

        # Are we producing plain text output?
        as_plain_text = 'text' == xslt_dom.xpath(
            'string(/xsl:stylesheet/xsl:output/@method)', namespaces={'xsl': 'http://www.w3.org/1999/XSL/Transform'})

        # Construct and apply the transformation
        transform = lxml.etree.XSLT(xslt_dom)
        result_dom = transform(data_dom)

        # Convert the transformation result into string
        if as_plain_text:
            result = str(result_dom)
        else:
            result = lxml.etree.tostring(result_dom, encoding=str, pretty_print=pretty_output)
            if result is None:
                result = ''
        logger.log("Done, XSLT transformation result is {} chars".format(len(result)))

        # Return the result
        return {output_param: result}
