"""Create and manipulate tree structures representing an author's dblp papers.
"""

from bigtree import Node  # type: ignore

from dblp_service.rdf_io.trees import match_attr_node  # type: ignore


def is_hasSignature_node(node: Node) -> bool:
    return match_attr_node(node, "hasSignature")
