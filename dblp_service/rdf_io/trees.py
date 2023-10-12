"""Create and manipulate authorship tree structures.



Typical usage example:

    foo = ClassFoo()
bar = foo.FunctionBar()
"""


import typing as t
from bigtree import Node  # type: ignore
import xml.etree.ElementTree as ET


def ends_with(s1: str, s2: str) -> bool:
    return s1.lower().endswith(s2.lower())


def match_attr_node(node: Node, pat: str) -> bool:
    return ends_with(node.node_name, pat)


def is_tree_attr_node(node: Node):
    return len(node.children) == 1 and len(node.children[0].children) == 0


def get_tree_attr(node: Node, keypat: str) -> t.Optional[str]:
    for chnode in node.children:
        if is_tree_attr_node(chnode) and match_attr_node(chnode, keypat):
            return chnode.children[0].node_name


def get_attr_value(node: Node) -> t.Optional[str]:
    assert is_tree_attr_node(node)
    return node.children[0].node_name


def match_attr_value(node: Node, keypat: str, valpat: str) -> bool:
    # assert is_tree_attr_node(node)
    matched = get_tree_attr(node, keypat)
    if matched is None:
        return False

    return ends_with(matched, valpat)


# def get_matching_attr(node: Node, keypat: str) -> t.Optional[str]:
#     for attr_node in node.children:
#         if attr_node.get_attr("type") != "attr":
#             continue
#         if match_attr_node(attr_node, keypat):
#             return attr_node.get_attr("value")


# def has_matching_attr(node: Node, keypat: str, valpat: str) -> bool:
#     attr_value = get_matching_attr(node, keypat)
#     if not attr_value:
#         return False

#     return attr_value.lower().endswith(valpat.lower())


def get_elem(n: Node) -> t.Optional[ET.Element]:
    return n.get_attr("element")


def set_elem(n: Node, elem: ET.Element) -> None:
    n.set_attrs(dict(element=elem))


def has_elem(n: Node) -> bool:
    return get_elem(n) is not None
