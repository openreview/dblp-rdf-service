"""Create a bibtex-style representation from an RDF-derived tree.
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

from dblp_service.rdf_io.tree_traversal import apply_handlers_to_tree
from dblp_service.rdf_io.tree_traverse_handlers import NameList, OutputBase, Publication


def output_to_bibtex(repr: OutputBase) -> Entry:
    assert isinstance(repr, Publication)
    fields: t.List[Field] = []
    for prop in repr.props:
        prop.key
        value = prop.value
        if isinstance(value, NameList):
            key = value.name_type
            names = [n.fullname for n in value.names]
            fields.append(Field(key, names))
        else:  # str
            fields.append(Field(prop.key, value))
    key = repr.key or "none"
    entry_type = repr.pub_type or "none"
    return Entry(
        entry_type=entry_type,
        key=key,
        fields=fields,
    )


def authorship_tree_to_bibtex(root: Node) -> Library:
    """ """
    library = Library()
    for subject in root.children:
        output = apply_handlers_to_tree(subject)
        entry = output_to_bibtex(output)
        library.add(entry)

    # as_string = write_string(
    #     library,
    #     prepend_middleware=[
    #         LatexEncodingMiddleware(allow_inplace_modification=True),
    #         MergeCoAuthors(allow_inplace_modification=True),
    #     ],
    # )

    return library
