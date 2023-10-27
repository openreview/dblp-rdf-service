import xml.etree.ElementTree as ET
import xml.dom.minidom


def print_xml(root: ET.Element):
    tree_out = ET.tostring(root, encoding="UTF-8")
    newXML = xml.dom.minidom.parseString(tree_out.decode("UTF-8"))
    pretty_xml = newXML.toprettyxml()
    print(pretty_xml)
