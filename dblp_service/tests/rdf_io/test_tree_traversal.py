from bigtree.tree.export import print_tree
from rich.pretty import pprint
from dblp_service.rdf_io.bibtex_transform import apply_handlers_to_tree
from dblp_service.rdf_io.tree_traverse_handlers import KeyValProp, NameList, NameSpec, Publication
from dblp_service.tests.rdf_io.test_tupledata import AUTHOR_1_TUPLES, AUTHOR_2_TUPLES

from ..helpers import get_author_tree_from_string


def test_traverse_has_signature():
    tuples = AUTHOR_1_TUPLES

    tree = get_author_tree_from_string(tuples)

    output = apply_handlers_to_tree(tree)

    expected = Publication(
        pub_type="Publication",
        key=None,
        props=[
            KeyValProp(
                key="author",
                value=NameList(
                    name_type="author", names=[NameSpec(name_type="author", fullname="Gregory Druck", ordinal=1)]
                ),
            )
        ],
    )

    assert output == expected


def test_traverse_has_multiple_signature():
    tuples = f"""
      {AUTHOR_1_TUPLES}
      {AUTHOR_2_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)
    output = apply_handlers_to_tree(tree)

    expected = Publication(
        pub_type="Publication",
        key=None,
        props=[
            KeyValProp(
                key="author",
                value=NameList(
                    name_type="author",
                    names=[
                        NameSpec(name_type="author", fullname="Gregory Druck", ordinal=1),
                        NameSpec(name_type="author", fullname="Kuzman Ganchev", ordinal=2),
                    ],
                ),
            )
        ],
    )

    assert output == expected
