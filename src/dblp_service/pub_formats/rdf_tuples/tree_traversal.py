"""Utilities to convert a tree structure into an ADT representation.
"""

import typing as t

from bigtree.node.node import Node
from dblp_service.pub_formats.rdf_tuples.dblp_repr import (
    AppendField,
    DblpRepr,
    HandlerType,
    UpdateOperation,
    SetField,
    InitFields,
)

from dblp_service.pub_formats.rdf_tuples.tree_traversal_viewer import StepViewer
from dblp_service.pub_formats.rdf_tuples.tree_traverse_handlers import AuthorPropertyHandlers
from dblp_service.pub_formats.rdf_tuples.trees import get_repr, iter_subj_obj_relationships, set_repr, simplify_urlname
from dblp_service.lib.log import create_logger


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
    handler = f'isA_{rel}'
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func

    return None


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
    handler = f'hasA_{rel}'
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func

    return None


def run_op(op: UpdateOperation, nsubj: Node):
    subj_repr = get_repr(nsubj)
    match op:
        case SetField(field, value, overwrite=do_overwrite):
            assert subj_repr is not None
            if field not in subj_repr or do_overwrite:
                subj_repr[field] = value

        case AppendField(field, value):
            assert subj_repr is not None
            subj_repr.setdefault(field, []).append(value)

        case InitFields(value, replace=doreplace):
            if subj_repr is None or doreplace:
                set_repr(nsubj, value)

        case _:
            raise Exception(f'Unknown UpdateOperation {op}')


def all_authorship_trees_to_reprs(root: Node) -> t.List[DblpRepr]:
    """
    Convert an authorship tree to an intermediate repr.

    Args:
        root (Node): The root node of the authorship tree.

    Returns:
        List[DblpRepr]: A list of reprs for each child of the root node.
    """
    return [authorship_tree_to_dblp_repr(subject) for subject in root.children]


def authorship_tree_to_dblp_repr(root: Node) -> DblpRepr:
    """
    Traverse the authorship tree and return an intermediate encoding.

    Args:
        root (Node): The root node of the authorship tree.

    Returns:
        DblpRepr: The representation of the authorship tree.
    """
    handlers = AuthorPropertyHandlers()

    __sv = StepViewer(interactive=False)

    try:
        # First time through, handle the 'isA' properties
        for nsubj, isA_rel, nobj in iter_subj_obj_relationships(root):
            if isA_rel.node_name != 'isA':
                continue

            __sv.scrutinees(nsubj, isA_rel, nobj)

            if func := get_isA_handler(nobj, handlers):
                __sv.handler(func)
                if op := func(nsubj, nobj):
                    run_op(op, nsubj)
                    __sv.ran_op(op)

            __sv.render_output()

        # Second time through, handle the 'hasA' properties
        for nsubj, hasA_rel, nobj in iter_subj_obj_relationships(root):
            if hasA_rel.node_name == 'isA':
                continue

            __sv.scrutinees(nsubj, hasA_rel, nobj)

            if func := get_hasA_handler(hasA_rel, handlers):
                __sv.handler(func)
                if op := func(hasA_rel, nobj):
                    run_op(op, nsubj)
                    __sv.ran_op(op)

            __sv.render_output()

        __sv.done()

        assert (root_entry := get_repr(root)) is not None

        return root_entry
    except Exception as e:
        print(f'exception was {e}')
        raise
