#!/usr/bin/env python3

from bigtree.node.node import Node
import typing as t

from dblp_service.rdf_io.queries import AuthorTuple, create_tree_from_tuples


def create_tree_from_tuplestrs(strs: t.List[str]) -> Node:
    tuples: t.List[AuthorTuple] = [eval(f"AuthorTuple{s}") for s in strs]
    return create_tree_from_tuples(tuples)


def get_author_tree(strs: t.List[str]) -> Node:
    tree = create_tree_from_tuplestrs(strs)
    assert len(tree.children) == 1
    atree = tree.children[0]
    return atree


def get_author_tree_from_string(block: str) -> Node:
    lines = [line.strip() for line in block.split("\n") if line.strip()]
    return get_author_tree(lines)
