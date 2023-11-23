#!/usr/bin/env python3

from bigtree.tree.export import print_tree
from bigtree.tree.construct import list_to_tree

from dblp_service.pub_formats.rdf_tuples.trees import get_nth_descendent, iter_subj_obj_relationships



def test_iter_subj_obj_relationships_simple():
    path_list = [
        "sub1/rel1/obj11",
        "sub1/rel1/obj12",
        "sub1/rel2/obj21",
    ]
    expected = [
        "sub1 rel1 obj11",
        "sub1 rel1 obj12",
        "sub1 rel2 obj21",
    ]
    root = list_to_tree(path_list)
    for i, (n1, n2, n3) in enumerate(iter_subj_obj_relationships(root)):
        actual = f"{n1.node_name} {n2.node_name} {n3.node_name}"
        assert actual == expected[i]


def test_iter_subj_obj_relationships_nested():
    path_list = [
        "s/r/so/r1/o",
        "s/r/so/r2/o",
    ]
    expected = [
        "so r1 o",
        "so r2 o",
        "s r so",
    ]
    root = list_to_tree(path_list)
    print_tree(root)
    for i, (n1, n2, n3) in enumerate(iter_subj_obj_relationships(root)):
        actual = f"{n1.node_name} {n2.node_name} {n3.node_name}"
        assert actual == expected[i]


def test_iter_subj_obj_relationships_depths():
    examples = [
        ["sub1/rel1/obj1"],
        ["r1/sub1/rel1/obj1"],
        ["r1/r2/sub1/rel1/obj1"],
    ]

    for exnum, example in enumerate(examples):
        root = list_to_tree(example)

        desc = get_nth_descendent(root, exnum)
        assert desc is not None
        for n1, n2, n3 in iter_subj_obj_relationships(desc):
            assert n1.node_name == "sub1"
            assert n2.node_name == "rel1"
            assert n3.node_name == "obj1"
