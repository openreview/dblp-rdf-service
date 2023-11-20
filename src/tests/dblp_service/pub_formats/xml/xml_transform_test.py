

from bigtree.tree.export import print_tree


from dblp_service.pub_formats.rdf_tuples.tree_traversal import authorship_tree_to_dblp_repr
from dblp_service.pub_formats.xml.xml_transform import dblp_repr_to_xml
from dblp_service.pub_formats.xml.xml_utils import print_xml

from tests.dblp_service.pub_formats.rdf_tuples.tupledata import (
    AUTHOR_1_TUPLES,
    AUTHOR_2_TUPLES,
    AUTHOR_3_TUPLES,
    AUTHOR_ID_TUPLES,
    PUBLICATION_ID_TUPLES,
    RESOURCE_IDENTIFIER_TUPLES,
    TITLE_VENUE_TUPLES,
)

from tests.helpers import (
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
