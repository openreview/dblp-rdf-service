"""Utilities to convert a tree structure into an ADT representation.
"""

import typing as t

from bigtree.node.node import Node
from bigtree.tree.export import print_tree
from dblp_service.dblp_io.rdf_io.dblp_repr import UpdateOperation
from dblp_service.dblp_io.rdf_io.dblp_repr import (
    AppendField,
    DblpRepr,
    HandlerType,
    Publication,
    WriteReprField,
    EmitRepr,
)
from dblp_service.dblp_io.rdf_io.tree_traverse_handlers import AuthorPropertyHandlers
from dblp_service.dblp_io.rdf_io.trees import iter_subject_triples, simplify_urlname
from dblp_service.lib.predef.log import create_logger


log = create_logger(__file__)


def get_isA_handler(node: Node, handlers: AuthorPropertyHandlers) -> t.Optional[HandlerType]:
    """
    Retrieve the handler for 'isA' relationships based on the node's name.

    Args:
        node (Node): The node to retrieve the handler for.
        handlers (AuthorPropertyHandlers): The handlers for authorship properties.

    Returns:
        Callable or None: The handler function if it exists and is callable, otherwise None.
    """
    rel = simplify_urlname(node.node_name)
    handler = f"isA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func


def get_hasA_handler(node: Node, handlers: AuthorPropertyHandlers) -> t.Optional[HandlerType]:
    """
    Retrieve the handler for 'hasA' relationships based on the node's name.

    Args:
        node (Node): The node to retrieve the handler for.
        handlers (AuthorPropertyHandlers): The handlers for authorship properties.

    Returns:
        Callable or None: The handler function if it exists and is callable, otherwise None.
    """
    rel = simplify_urlname(node.node_name)
    handler = f"hasA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func

    return None


def run_op(op: object, nsubj: Node):
    match op:
        case WriteReprField(field, value, overwrite=do_overwrite):
            if do_overwrite:
                elem = nsubj.get_attr("elem")
                elem[field] = value

        case AppendField(field, value):
            elem: DblpRepr = nsubj.get_attr("elem")
            elem.setdefault(field, []).append(value)

        case EmitRepr(target, value, replace=doreplace):
            if doreplace:
                target.set_attrs(dict(elem=value))

        case _:
            pass


def authorship_tree_to_dblp_repr(root: Node) -> DblpRepr:
    """
    Traverse the authorship tree and return an intermediate encoding.

    Args:
        root (Node): The root node of the authorship tree.

    Returns:
        DblpRepr: The representation of the authorship tree.
    """
    handlers = AuthorPropertyHandlers()
    init_pub = Publication()
    root.set_attrs(dict(elem=init_pub))

    # First time through, handle the 'isA' properties
    for nsubj, isA_rel, nobj in iter_subject_triples(root):
        if isA_rel.node_name != "isA":
            continue

        if func := get_isA_handler(nobj, handlers):
            if op := func(nsubj, nobj):
                run_op(op, nsubj)

    # Second time through, handle the 'hasA' properties
    for nsubj, hasA_rel, nobj in iter_subject_triples(root):
        if hasA_rel.node_name == "isA":
            continue

        if func := get_hasA_handler(hasA_rel, handlers):
            if op := func(hasA_rel, nobj):
                run_op(op, nsubj)

    root_entry = root.get_attr("elem")

    assert root_entry is not None
    return root_entry


def all_authorship_trees_to_reprs(root: Node) -> t.List[DblpRepr]:
    """
    Convert an authorship tree to an intermediate repr.

    Args:
        root (Node): The root node of the authorship tree.

    Returns:
        List[DblpRepr]: A list of reprs for each child of the root node.
    """
    return [authorship_tree_to_dblp_repr(subject) for subject in root.children]
