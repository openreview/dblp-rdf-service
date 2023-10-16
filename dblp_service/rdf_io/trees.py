"""Create and manipulate RDF-derived tree structures.
"""


import typing as t
import xml.etree.ElementTree as ET

from bigtree.node.node import Node
from bigtree.utils.iterators import postorder_iter


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


def get_elem(n: Node) -> t.Optional[ET.Element]:
    return n.get_attr("element")


def set_elem(n: Node, elem: ET.Element) -> None:
    n.set_attrs(dict(element=elem))


def has_elem(n: Node) -> bool:
    return get_elem(n) is not None


SubjectObjectRelationship = t.Tuple[Node, str, Node]
SubjectRelObjectNodes = t.Tuple[Node, Node, Node]


def simplify_relation(rel: str) -> str:
    if "/" in rel:
        rel = rel.split("/")[-1]

    if "#" in rel:
        rel = rel.split("#")[-1]
    return rel


def iter_subject_triples(sub_node: Node) -> t.Generator[SubjectRelObjectNodes, None, None]:
    """Generate all sub->rel->obj triples with sub_node as root.

    Given a tree like
        sub1
        └── rel1
            └── obj1

    create a generator that yields...

    sub_node - node representing root subject over # of relations
    """
    # traverse to a depth of 3, relative to sub_node
    max_depth = sub_node.depth + 2

    for desc_node in postorder_iter(sub_node, max_depth=max_depth):
        relative_depth = (desc_node.depth - sub_node.depth) + 1
        if relative_depth < 3:
            continue
        if desc_node.children:
            for sub in iter_subject_triples(desc_node):
                yield sub

        obj_node = desc_node
        rel_node = obj_node.parent
        assert rel_node is not None
        yield (sub_node, rel_node, obj_node)


def get_nth_descendent(node: Node, n: int) -> t.Optional[Node]:
    desc = node
    for _ in range(n):
        if desc is None:
            return
        desc = desc.children[0] if desc.children else None
    return desc
