from bibtexparser import Library, write_string
from bibtexparser.middlewares.names import MergeCoAuthors
from bibtexparser.middlewares import LatexEncodingMiddleware
from icecream import ic

from bibtexparser import Library, write_string

from dblp_service.dblp_io.rdf_io.tree_traversal_alt import authorship_tree_to_dblp_repr
from dblp_service.dblp_io.bibtex_output.bibtex_transform import dblp_repr_to_bibtex

from dblp_service.tests.dblp_io.rdf_io.test_tupledata import (
    AUTHOR_1_TUPLES,
    AUTHOR_2_TUPLES,
    AUTHOR_3_TUPLES,
    AUTHOR_ID_TUPLES,
    DRUCK_BIBTEX_ENTRY,
    PUBLICATION_ID_TUPLES,
    TITLE_VENUE_TUPLES,
)

from dblp_service.tests.helpers import (
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
    {TITLE_VENUE_TUPLES}
    {AUTHOR_1_TUPLES}
    {AUTHOR_2_TUPLES}
    {AUTHOR_3_TUPLES}
    {AUTHOR_ID_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)

    bibtex_entry = authorship_tree_to_dblp_repr(tree)
    entry = dblp_repr_to_bibtex(bibtex_entry)
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
