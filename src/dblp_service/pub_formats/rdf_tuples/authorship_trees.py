"""Create and manipulate tree structures representing an author's dblp papers.
"""


from bigtree.node.node import Node
from dblp_service.pub_formats.rdf_tuples.trees import match_attr_node  # type: ignore


def is_hasSignature_node(node: Node) -> bool:
    return match_attr_node(node, "hasSignature")
