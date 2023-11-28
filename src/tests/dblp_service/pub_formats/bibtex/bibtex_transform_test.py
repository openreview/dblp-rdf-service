from pprint import pp
from bibtexparser import Library, write_string # type: ignore
from bibtexparser.middlewares.names import MergeCoAuthors # type: ignore
from bibtexparser.middlewares import LatexEncodingMiddleware # type: ignore
from icecream import ic

# from bibtexparser import Library, write_string

from dblp_service.pub_formats.rdf_tuples.tree_traversal import authorship_tree_to_dblp_repr
from dblp_service.pub_formats.bibtex.bibtex_transform import dblp_repr_to_bibtex

from tests.dblp_service.pub_formats.rdf_tuples.tupledata import (
    AUTHOR_1_TUPLES,
    AUTHOR_2_TUPLES,
    AUTHOR_3_TUPLES,
    AUTHOR_ID_TUPLES,
    DRUCK_BIBTEX_ENTRY,
    PUBLICATION_ID_TUPLES,
    RESOURCE_IDENTIFIER_TUPLES,
    TITLE_VENUE_TUPLES,
)

from tests.helpers import (
    assert_fields_match,
    bibtex_str_to_library,
    get_author_tree_from_string,
    rdf_blocks_to_entry,
)


def test_bibtex_title_year():
    expected_entry = bibtex_str_to_library(DRUCK_BIBTEX_ENTRY).entries[0]
    actual_entry = rdf_blocks_to_entry([PUBLICATION_ID_TUPLES, TITLE_VENUE_TUPLES])

    assert_fields_match("title", actual_entry, expected_entry)
    assert_fields_match("year", actual_entry, expected_entry)


def test_bibtex_signature():
    expected_entry = bibtex_str_to_library(DRUCK_BIBTEX_ENTRY).entries[0]
    actual_entry = rdf_blocks_to_entry([PUBLICATION_ID_TUPLES, AUTHOR_1_TUPLES])

    ic(expected_entry)
    ic(actual_entry)


def test_bibtex_full():
    tuples = f"""
    {PUBLICATION_ID_TUPLES}
    {RESOURCE_IDENTIFIER_TUPLES}
    {TITLE_VENUE_TUPLES}
    {AUTHOR_1_TUPLES}
    {AUTHOR_2_TUPLES}
    {AUTHOR_3_TUPLES}
    {AUTHOR_ID_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)

    bibtex_entry = authorship_tree_to_dblp_repr(tree, step_debug=False)
    pp(bibtex_entry)
    entry = dblp_repr_to_bibtex(bibtex_entry)
    pp(entry)
    library = Library()

    library.add(entry)
    as_string = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )

    print(as_string)
