"""Create a bibtex-style representation from intermediate representation.
"""

import typing as t
from bigtree.node.node import Node

from bibtexparser import Library, write_string  # type: ignore
from bibtexparser.middlewares import LatexEncodingMiddleware  # type: ignore
from bibtexparser.middlewares.names import MergeCoAuthors  # type: ignore
from bibtexparser.model import (Entry, Field)  # type: ignore

from dblp_service.pub_formats.rdf_tuples.dblp_repr import DblpRepr, Publication
from dblp_service.pub_formats.rdf_tuples.tree_traversal import all_authorship_trees_to_reprs

from dblp_service.lib.log import create_logger


log = create_logger(__file__)

fake_key = 1


def next_fake_key() -> str:
    global fake_key
    k = f"key#{fake_key}"
    fake_key = fake_key + 1
    return k


def dblp_repr_to_bibtex(repr: DblpRepr) -> Entry:
    assert isinstance(repr, Publication)
    fields: t.List[Field] = []

    entry_key = next_fake_key()
    entry_type = "TODO"

    for key, value in repr.items():
        match key:
            case "key":
                entry_key = value
            case "type":
                entry_type = value
            case "author":
                names = [a["fullname"] for a in value]
                fields.append(Field(key, names))
                pass
            case _:
                fields.append(Field(key, value))

    entry = Entry(
        entry_type=entry_type,
        key=entry_key,
        fields=fields,
    )
    return entry


def dblp_reprs_to_bibtex_library(reprs: t.List[DblpRepr]) -> Library:
    """ """
    library = Library()
    for repr in reprs:
        entry = dblp_repr_to_bibtex(repr)
        library.add(entry)

    return library


def authorship_tree_to_bibtex(root: Node) -> Library:
    """ """
    dblp_reprs = all_authorship_trees_to_reprs(root, False)
    library = Library()
    for repr in dblp_reprs:
        entry = dblp_repr_to_bibtex(repr)
        library.add(entry)

    return library


def library_to_str(library: Library):
    as_string = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )
    return as_string


def repr_to_bibtex_str(repr: DblpRepr) -> str:
    lib = dblp_reprs_to_bibtex_library([repr])
    return library_to_str(lib)


def print_library(library: Library):
    print(library_to_str(library))
