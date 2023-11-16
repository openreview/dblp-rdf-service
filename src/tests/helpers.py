#!/usr/bin/env python3

from dataclasses import dataclass
from bibtexparser import Library, parse_string  # type: ignore
from bibtexparser.middlewares.names import SeparateCoAuthors  # type: ignore
from bibtexparser.model import Entry  # type: ignore
from bigtree.node.node import Node
import typing as t
from bigtree.tree.export import print_tree

from icecream import ic
from rich.pretty import pprint

from dblp_service.dblp_io.rdf_io.queries import AuthorTuple, create_tree_from_tuples
from dblp_service.dblp_io.rdf_io.tree_traversal import authorship_tree_to_dblp_repr


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


@dataclass
class BibtexOutput:
    tree: Node
    tree_str: str
    entry: Entry
    bibtex_str: str


def rdf_to_bibtex(tuplestr: str) -> BibtexOutput:
    tree = get_author_tree_from_string(tuplestr)
    print_tree(tree, all_attrs=True)

    dblp_repr = authorship_tree_to_dblp_repr(tree)
    ic()
    pprint(dblp_repr)
    # bibtex_str = repr_to_bibtex_str(dblp_repr)
    # entry = dblp_repr_to_bibtex(dblp_repr)
    entry = Entry(entry_type="none", key="none", fields=[])
    bibtex_str = "TODO"

    return BibtexOutput(tree=tree, tree_str="", entry=entry, bibtex_str=bibtex_str)
    # return BibtexOutput(tree=tree, tree_str="", bibtex_str="todo")


def assert_fields_match(field: str, actual: Entry, expected: Entry):
    expected_field = expected.fields_dict[field]
    expected_value = expected_field.value

    actual_field = actual.fields_dict[field]
    actual_value = actual_field.value

    assert actual_value == expected_value


def bibtex_str_to_library(bibtex_str: str) -> Library:
    return parse_string(
        bibtex_str,
        append_middleware=[
            SeparateCoAuthors(allow_inplace_modification=True),
        ],
    )


def rdf_blocks_to_entry(rdf_blocks: t.List[str]) -> Entry:
    rdf = "\n".join(rdf_blocks)
    output = rdf_to_bibtex(rdf)
    return output.entry

## TODO combine these _fqn funcs into one
P = t.ParamSpec("P")
def callable_fqn(fn: t.Callable[P, t.Any]) -> str:
    m = fn.__module__
    n = fn.__name__
    return f'{m}.{n}'

def method_fqn(method: t.Callable[P, t.Any]) -> str:
    mod = method.__module__
    qn = method.__qualname__
    return f'{mod}.{qn}'
