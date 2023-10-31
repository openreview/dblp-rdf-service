from pprint import pprint as pp

from bigtree.tree.export import print_tree
from dblp_service.dblp_io.rdf_io.dblp_repr_alt import Publication
from dblp_service.dblp_io.rdf_io.tree_traversal_alt import authorship_tree_to_dblp_repr
from dblp_service.tests.dblp_io.rdf_io.test_tupledata import AUTHOR_1_TUPLES, AUTHOR_2_TUPLES, PUBLICATION_ID_TUPLES, RESOURCE_IDENTIFIER_TUPLES
from dblp_service.tests.helpers import get_author_tree_from_string


def test_traverse_has_signature():
    tuples = AUTHOR_1_TUPLES

    tree = get_author_tree_from_string(tuples)

    output = authorship_tree_to_dblp_repr(tree)

    expected = {"author": [{"name_type": "author", "fullname": "Gregory Druck", "ordinal": 1}]}

    assert output == expected


def test_traverse_has_multiple_signature():
    tuples = f"""
      {AUTHOR_1_TUPLES}
      {AUTHOR_2_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)
    output = authorship_tree_to_dblp_repr(tree)

    expected = {
        "author": [
            {"name_type": "author", "fullname": "Gregory Druck", "ordinal": 1},
            {"fullname": "Kuzman Ganchev", "name_type": "author", "ordinal": 2},
        ]
    }

    assert output == expected

def test_traverse_resource_ids():
    tuples = f"""
      {RESOURCE_IDENTIFIER_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)

    output = authorship_tree_to_dblp_repr(tree)
    expected = {'key': 'DBLP:conf/acl/DruckGG11'}

    assert output == expected

def test_traverse_publication_type():
    tuples = f"""
      {PUBLICATION_ID_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)
    print_tree(tree, all_attrs=True)

    output = authorship_tree_to_dblp_repr(tree)
    pp(output)
    # expected = {'key': 'DBLP:conf/acl/DruckGG11'}

    # assert output == expected
