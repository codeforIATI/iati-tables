from collections import OrderedDict
from lxml import etree

from iatidata import sort_iati_element

def test_sort_iati_element():
    input_xml = '<iati-activity><iati-identifier>XXXXXXXX</iati-identifier><activity-status code="2"/><transaction><transaction-date iso-date="2024-01-25"/><transaction-type code="3"/></transaction><title><narrative xml:lang="en">XXXXXXXX</narrative></title></iati-activity>'
    element = etree.fromstring(input_xml)
    schema_dict = OrderedDict([
        ('iati-identifier', OrderedDict()),
        ('title', OrderedDict([('narrative', OrderedDict())])),
        ('activity-status', OrderedDict()),
        ('transaction', OrderedDict([('transaction-type', OrderedDict()), ('transaction-date', OrderedDict())])),
    ])

    sort_iati_element(element, schema_dict)

    expected_xml = b'<iati-activity><iati-identifier>XXXXXXXX</iati-identifier><title><narrative xml:lang="en">XXXXXXXX</narrative></title><activity-status code="2"/><transaction><transaction-type code="3"/><transaction-date iso-date="2024-01-25"/></transaction></iati-activity>'
    assert etree.tostring(element) == expected_xml
