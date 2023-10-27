"""Utilities to convert a tree structure into an ADT representation.
"""

import typing as t

from bigtree.node.node import Node
from bigtree.tree.export import print_tree
from dblp_service.dblp_io.rdf_io.dblp_repr import DblpRepr, KeyValProp, Publication
from dblp_service.dblp_io.rdf_io.tree_traverse_handlers import AuthorshipPropertyHandlers
from dblp_service.dblp_io.rdf_io.trees import iter_subject_triples, simplify_urlname
from dblp_service.lib.predef.log import create_logger

from icecream import ic

log = create_logger(__file__)


def get_isA_handler(
    node: Node, handlers: AuthorshipPropertyHandlers
) -> t.Optional[t.Callable[[Node, Node], t.Optional[DblpRepr]]]:
    """
    Retrieve the handler for 'isA' relationships based on the node's name.

    Args:
        node (Node): The node to retrieve the handler for.
        handlers (AuthorshipPropertyHandlers): The handlers for authorship properties.

    Returns:
        Callable or None: The handler function if it exists and is callable, otherwise None.
    """
    rel = simplify_urlname(node.node_name)
    handler = f"isA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func


def get_hasA_handler(
    node: Node, handlers: AuthorshipPropertyHandlers
) -> t.Optional[t.Callable[[Node, Node], t.Optional[DblpRepr]]]:
    """
    Retrieve the handler for 'hasA' relationships based on the node's name.

    Args:
        node (Node): The node to retrieve the handler for.
        handlers (AuthorshipPropertyHandlers): The handlers for authorship properties.

    Returns:
        Callable or None: The handler function if it exists and is callable, otherwise None.
    """
    rel = simplify_urlname(node.node_name)
    handler = f"hasA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func

def authorship_tree_to_dblp_repr(root: Node) -> DblpRepr:
    """
    Traverse the authorship tree and return an intermediate encoding.

    Args:
        root (Node): The root node of the authorship tree.

    Returns:
        DblpRepr: The representation of the authorship tree.
    """
    handlers = AuthorshipPropertyHandlers()

    # First time through, handle the 'isA' properties
    for nsubj, isA_rel, nobj in iter_subject_triples(root):
        if isA_rel.node_name != "isA":
            continue

        func = get_isA_handler(nobj, handlers)
        if func:
            created = func(nsubj, nobj)
            if created:
                # log.info(f"init isA {created}")
                nsubj.set_attrs(dict(entry=created))
                ic(created, nsubj, 'from tree')
                print_tree(isA_rel, all_attrs=True)
                print()

    # Second time through, handle the 'hasA' properties
    for nsubj, hasA_rel, nobj in iter_subject_triples(root):
        if hasA_rel.node_name == "isA":
            continue

        func = get_hasA_handler(hasA_rel, handlers)
        if func:
            created = func(hasA_rel, nobj)
            if created:
                log.info(f"hasA {created}")
                prior = nsubj.get_attr("entry")
                combined = created
                if prior is not None:
                    combined = prior.merge(created) if prior is not None else created
                    log.info(f"  == {combined}")
                nsubj.set_attrs(dict(entry=combined))
                ic(created, nsubj, 'from tree')
                print_tree(hasA_rel, all_attrs=True)
                print()

    root_entry = root.get_attr("entry")

    assert root_entry is not None
    return root_entry


def has_prop(pub: Publication, prop: KeyValProp) -> bool:
    """
    Check if a publication has a specific property.

    Args:
        pub (Publication): The publication to check.
        prop (KeyValProp): The property to look for.

    Returns:
        bool: True if the publication has the property, otherwise False.
    """
    def is_match(pub_prop: KeyValProp) -> bool:
        return pub_prop.key == prop.key

    matched_props = list(filter(is_match, pub.props))
    return len(matched_props) > 0


def get_prop(pub: Publication, prop_key: str) -> t.Optional[KeyValProp]:
    """
    Retrieve a specific property from a publication.

    Args:
        pub (Publication): The publication to retrieve the property from.
        prop_key (str): The key of the property to retrieve.

    Returns:
        KeyValProp or None: The property if it exists, otherwise None.
    """
    def is_match(pub_prop: KeyValProp) -> bool:
        return pub_prop.key == prop_key

    matched_props = list(filter(is_match, pub.props))
    if len(matched_props) == 0:
        return None
    return matched_props[0]


def all_authorship_trees_to_reprs(root: Node) -> t.List[DblpRepr]:
    """
    Convert an authorship tree to an intermediate repr.

    Args:
        root (Node): The root node of the authorship tree.

    Returns:
        List[DblpRepr]: A list of reprs for each child of the root node.
    """
    return [authorship_tree_to_dblp_repr(subject) for subject in root.children]
