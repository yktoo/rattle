from etl import config
from etl.handlers import xslt


# The default configuration
_config = {
    'input_param':  'in',
    'output_param': 'out',
    'in':
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<test>'
        '  <container>'
        '    <entry type="A" sort="B" name="C" value="4">text_1</entry>'
        '    <entry type="D" sort="E" name="F" value="5">text_2</entry>'
        '    <entry type="G" sort="H" name="I" value="6">text_3</entry>'
        '    <entry type="J" sort="K" name="L" value="7">text_4</entry>'
        '  </container>'
        '</test>',
    'xslt_text':
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">'
        '  <xsl:output method="text" omit-xml-declaration="yes" media-type="string"/>'
        '  <xsl:template match="/">'
        '    <xsl:for-each select="test/container/entry">'
        '      <xsl:value-of select="@type"/>'
        '      <xsl:text>,</xsl:text>'
        '      <xsl:value-of select="@sort"/>'
        '      <xsl:text>,</xsl:text>'
        '      <xsl:value-of select="@name"/>'
        '      <xsl:text>,</xsl:text>'
        '      <xsl:value-of select="@value"/>'
        '      <xsl:text>,</xsl:text>'
        '      <xsl:value-of select="."/>'
        '      <xsl:text>&#xa;</xsl:text>'
        '    </xsl:for-each>'
        '  </xsl:template>'
        '</xsl:stylesheet>',
    'xslt_xml':
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">'
        '  <xsl:template match="/">'
        '    <data>'
        '      <xsl:for-each select="test/container/entry">'
        '        <item>'
        '          <type><xsl:value-of select="@type"/></type>'
        '          <sort><xsl:value-of select="@sort"/></sort>'
        '          <name><xsl:value-of select="@name"/></name>'
        '          <value><xsl:value-of select="@value"/></value>'
        '          <text><xsl:value-of select="."/></text>'
        '        </item>'
        '      </xsl:for-each>'
        '    </data>'
        '  </xsl:template>'
        '</xsl:stylesheet>'
}

def test_text_output():
    """handlers.xslt: test plain-text output"""
    result = xslt.Handler().run(config.Config(_config, xslt_param='xslt_text'))
    print(result)
    assert result['out'] == \
        'A,B,C,4,text_1\n' \
        'D,E,F,5,text_2\n' \
        'G,H,I,6,text_3\n' \
        'J,K,L,7,text_4\n'


def test_xml_output_unformatted():
    """handlers.xslt: test unformatted XML output"""
    result = xslt.Handler().run(config.Config(_config, xslt_param='xslt_xml'))
    print(result)
    assert result['out'] == \
        '<data>'                                                                                     \
        '<item><type>A</type><sort>B</sort><name>C</name><value>4</value><text>text_1</text></item>' \
        '<item><type>D</type><sort>E</sort><name>F</name><value>5</value><text>text_2</text></item>' \
        '<item><type>G</type><sort>H</sort><name>I</name><value>6</value><text>text_3</text></item>' \
        '<item><type>J</type><sort>K</sort><name>L</name><value>7</value><text>text_4</text></item>' \
        '</data>'


def test_xml_output_formatted():
    """handlers.xslt: test formatted XML output"""
    result = xslt.Handler().run(config.Config(_config, xslt_param='xslt_xml', pretty_output=True))
    print(result)
    assert result['out'] == \
        '<data>\n'                  \
        '  <item>\n'                \
        '    <type>A</type>\n'      \
        '    <sort>B</sort>\n'      \
        '    <name>C</name>\n'      \
        '    <value>4</value>\n'    \
        '    <text>text_1</text>\n' \
        '  </item>\n'               \
        '  <item>\n'                \
        '    <type>D</type>\n'      \
        '    <sort>E</sort>\n'      \
        '    <name>F</name>\n'      \
        '    <value>5</value>\n'    \
        '    <text>text_2</text>\n' \
        '  </item>\n'               \
        '  <item>\n'                \
        '    <type>G</type>\n'      \
        '    <sort>H</sort>\n'      \
        '    <name>I</name>\n'      \
        '    <value>6</value>\n'    \
        '    <text>text_3</text>\n' \
        '  </item>\n'               \
        '  <item>\n'                \
        '    <type>J</type>\n'      \
        '    <sort>K</sort>\n'      \
        '    <name>L</name>\n'      \
        '    <value>7</value>\n'    \
        '    <text>text_4</text>\n' \
        '  </item>\n'               \
        '</data>\n'
