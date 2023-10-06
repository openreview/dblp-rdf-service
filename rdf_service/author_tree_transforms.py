import xml.etree.ElementTree as ET
import xml.dom.minidom
from bigtree import Node  # type: ignore
from bigtree.utils.iterators import preorder_iter

from rich import print

from rdf_service.trees import get_attr_value, get_elem, get_tree_attr, has_elem, is_tree_attr_node, match_attr_node, match_attr_value, set_elem


def authorship_tree_to_xml(root: Node) -> ET.Element:
    for n in preorder_iter(root, has_elem):
        if n.depth == 1:
            continue

        elem = get_elem(n)
        assert elem is not None

        containing_elems = [get_elem(a) for a in n.ancestors if has_elem(a)]

        nearest_elem = containing_elems[0]
        assert nearest_elem is not None
        nearest_elem.append(elem)

    rootelem = get_elem(root);
    assert rootelem is not None
    return rootelem


def rewrite_publication_node(node: Node):
    set_elem(node, create_xml_root_elem(node))
    rewrite_attr_nodes(node)
    rewrite_hasSignature_nodes(node)

def rewrite_authorship_tree(root: Node):
    set_elem(root, ET.Element("dblpperson"))
    for node in root.children:
        rewrite_publication_node(node)


def is_hasSignature_node(node: Node) -> bool:
    return match_attr_node(node, "hasSignature")


def rewrite_hasSignature_nodes(tree: Node):
    for node in filter(is_hasSignature_node, tree.children):
        rewrite_hasSignature_node(node)


def rewrite_hasSignature_node(tree: Node):
    assert is_hasSignature_node(tree)
    for bnode in tree.children:
        author_name = get_tree_attr(bnode, "signatureDblpName")
        author_uri = get_tree_attr(bnode, "signatureCreator")
        assert author_name is not None
        assert author_uri is not None
        author_elem = ET.Element("author")
        author_elem.text = author_name
        bnode.set_attrs(dict(element=author_elem))

        # hasIdentifier . b52 . hasLiteralValue = 'conf/.../Druck24


def rewrite_attr_nodes(tree: Node):
    for attr_node in filter(is_tree_attr_node, tree.children):
        rewrite_attr_node(attr_node)


rdf_to_xml_mapping2 = {
    "yearOfPublication": "year",
    "title": "title",
    "pagination": "pages",
    "publishedIn": "booktitle",
    "publishedInBook": "booktitle",
    "publishedInJournal": "journal",
    "publishedInJournalVolume": "volume",
    # "bibtexType": "",
    # "primaryDocumentPage": "",
}


def rewrite_attr_node(tree: Node):
    for attr_name, elem_name in rdf_to_xml_mapping2.items():
        if match_attr_node(tree, attr_name):
            elem = ET.Element(elem_name)
            text = get_attr_value(tree)
            elem.text = text
            tree.set_attrs(dict(element=elem))



def uri_last_path(s: str) -> str:
    if not s:
        return ""
    if s.startswith("http"):
        sp = s.split("/")
        return sp[-1]
    return s


def create_xml_root_elem(node: Node):
    if match_attr_value(node, "bibtexType", "InProceedings"):
        return ET.Element("inproceedings")

    return ET.Element("article-todo")

def print_xml(root: ET.Element):
    tree_out = ET.tostring(root, encoding="UTF-8")
    newXML = xml.dom.minidom.parseString(tree_out.decode("UTF-8"))
    pretty_xml = newXML.toprettyxml()
    print(pretty_xml)

# rdf_to_xml_mapping = {
#     "year": ["yearOfPublication"],
#     "title": ["title"],
#     "pages": ["pagination"],
#     "booktitle": ["publishedIn", "publishedInBook"],
#     "journal": ["publishedInJournal"],
#     "volume": ["publishedInJournalVolume"],
#     # "bibtexType": "",
#     # "primaryDocumentPage": "",
# }
# def add_xml_elems(xroot: ET.Element, node: Node):
#     for elem_name, attr_names in rdf_to_xml_mapping.items():
#         potential_attrs = [att for att in [get_matching_attr(node, n) for n in attr_names] if att is not None]

#         if len(potential_attrs) == 0:
#             continue
#         attr = potential_attrs[0]
#         elem = ET.Element(elem_name)
#         elem.text = attr
#         xroot.append(elem)
