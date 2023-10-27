"""Create and manipulate tree structures representing an author's dblp papers.
"""


from bigtree.node.node import Node
from dblp_service.dblp_io.rdf_io.trees import match_attr_node  # type: ignore


def is_hasSignature_node(node: Node) -> bool:
    return match_attr_node(node, "hasSignature")
