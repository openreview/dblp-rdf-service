"""Create and manipulate RDF-derived tree structures.
"""


import typing as t
import xml.etree.ElementTree as ET

from bigtree.node.node import Node
from bigtree.utils.iterators import postorder_iter

from dblp_service.pub_formats.rdf_tuples.dblp_repr import DblpRepr


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
    return None


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
    elem: t.Optional[ET.Element] = n.get_attr('element')
    return elem


def set_elem(n: Node, elem: ET.Element) -> None:
    n.set_attrs(dict(element=elem))


def has_elem(n: Node) -> bool:
    return get_elem(n) is not None


def get_repr(n: Node) -> t.Optional[DblpRepr]:
    repr: t.Optional[DblpRepr] = n.get_attr('repr')
    return repr


def remove_repr(n: Node) -> t.Optional[DblpRepr]:
    repr = get_repr(n)
    delattr(n, 'repr')
    return repr


def set_repr(n: Node, repr: DblpRepr) -> None:
    n.set_attrs(dict(repr=repr))


SubjectObjectRelationship = t.Tuple[Node, str, Node]
SubjectRelObjectNodes = t.Tuple[Node, Node, Node]


def simplify_urlname(rel: str) -> str:
    if '/' in rel:
        rel = rel.split('/')[-1]

    if '#' in rel:
        rel = rel.split('#')[-1]
    return rel


def iter_subj_obj_relationships(sub_node: Node) -> t.Generator[SubjectRelObjectNodes, None, None]:
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
            for sub in iter_subj_obj_relationships(desc_node):
                yield sub

        obj_node = desc_node
        rel_node = obj_node.parent
        assert rel_node is not None
        yield (sub_node, rel_node, obj_node)


def get_nth_descendent(node: Node, n: int) -> t.Optional[Node]:
    desc: t.Optional[Node] = node
    for _ in range(n):
        if desc is None:
            return None
        desc = desc.children[0] if desc.children else None
    return desc
