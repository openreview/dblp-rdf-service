
from pprint import pp

from bigtree.tree.export import print_tree


from dblp_service.dblp_io.rdf_io.tree_traversal import authorship_tree_to_dblp_repr
from dblp_service.dblp_io.xml_output.xml_transform import dblp_repr_to_xml
from dblp_service.dblp_io.xml_output.xml_utils import print_xml

from dblp_service.tests.dblp_io.rdf_io.test_tupledata import (
    AUTHOR_1_TUPLES,
    AUTHOR_2_TUPLES,
    AUTHOR_3_TUPLES,
    AUTHOR_ID_TUPLES,
    DRUCK_BIBTEX_ENTRY,
    PUBLICATION_ID_TUPLES,
    RESOURCE_IDENTIFIER_TUPLES,
    TITLE_VENUE_TUPLES,
)

from dblp_service.tests.helpers import (
    assert_fields_match,
    get_author_tree_from_string,
)

def test_xml_full():
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
    print_tree(tree)
    repr = authorship_tree_to_dblp_repr(tree)
    as_xml = dblp_repr_to_xml(repr)
    print_xml(as_xml)
