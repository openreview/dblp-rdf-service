"""Create a bibtex-style representation from intermediate representation.
"""

import typing as t
from bigtree.node.node import Node

from bibtexparser import Library, write_string
from bibtexparser.middlewares import LatexEncodingMiddleware
from bibtexparser.middlewares.names import MergeCoAuthors
from bibtexparser.model import (
    Entry,
    Field,
)

from dblp_service.lib.predef.log import create_logger

from dblp_service.rdf_io.tree_traversal import authorship_tree_to_repr
from dblp_service.rdf_io.dblp_repr import DblpRepr, Publication

log = create_logger(__file__)

fake_key = 1


def next_fake_key() -> str:
    global fake_key
    k = f"key#{fake_key}"
    fake_key = fake_key + 1
    return k


def dblprepr_to_bibtex(repr: DblpRepr) -> Entry:
    assert isinstance(repr, Publication)
    fields: t.List[Field] = []

    for prop in repr.props:
        value = prop.value
        if isinstance(value, t.List):
            key = prop.key
            fields.append(Field(key, value))
        else:  # str
            if prop.key in [f.key for f in fields]:
                continue
            fields.append(Field(prop.key, value))

    key = repr.key or next_fake_key()
    entry_type = repr.pub_type or "none"
    entry = Entry(
        entry_type=entry_type,
        key=key,
        fields=fields,
    )
    return entry


def dblp_reprs_to_bibtex_library(reprs: t.List[DblpRepr]) -> Library:
    """ """
    library = Library()
    for repr in reprs:
        entry = dblprepr_to_bibtex(repr)
        library.add(entry)

    return library


def authorship_tree_to_bibtex(root: Node) -> Library:
    """ """
    dblp_reprs = authorship_tree_to_repr(root)
    library = Library()
    for repr in dblp_reprs:
        entry = dblprepr_to_bibtex(repr)
        library.add(entry)

    return library


def print_library(library: Library):
    as_string = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )
    print(as_string)
