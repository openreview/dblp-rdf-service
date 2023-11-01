"""Create an XML representation from an RDF-derived tree.
"""


import typing as t

import xml.etree.ElementTree as ET
from bigtree import Node  # type: ignore
from bigtree.utils.iterators import preorder_iter
from dblp_service.dblp_io.rdf_io.authorship_trees import is_hasSignature_node
from dblp_service.dblp_io.rdf_io.dblp_repr import DblpRepr, Publication

from dblp_service.dblp_io.rdf_io.trees import (
    get_attr_value,
    get_elem,
    get_tree_attr,
    has_elem,
    is_tree_attr_node,
    match_attr_node,
    match_attr_value,
    set_elem,
)


def dblp_repr_to_xml(repr: DblpRepr) -> ET.Element:
    assert isinstance(repr, Publication)
    child_elems: t.List[ET.Element] = []

    entry_key = "Key#0"
    entry_type = "TODO"

    for key, value in repr.items():
        match key:
            case "key":
                entry_key = value
            case "type":
                entry_type = value
            case "author":
                for a in value:
                    pid = a["pid"]
                    e = ET.Element("author", dict(pid=pid))
                    e.text = a["fullname"]
                    child_elems.append(e)
            case _:
                pass

    xml_root = ET.Element(entry_type, dict(key=entry_key))
    for c in child_elems:
        xml_root.append(c)

    return xml_root


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

    rootelem = get_elem(root)
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


rdf_to_xml_mapping = {
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
    for attr_name, elem_name in rdf_to_xml_mapping.items():
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
