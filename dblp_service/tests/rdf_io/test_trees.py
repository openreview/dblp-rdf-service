#!/usr/bin/env python3

from bigtree.tree.export import print_tree
from bigtree.tree.construct import list_to_tree

from dblp_service.rdf_io.trees import get_nth_descendent, iter_subnode_triples


def test_iter_subnode_triples_simple():
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
    for i, (n1, n2, n3) in enumerate(iter_subnode_triples(root)):
        actual = f"{n1.node_name} {n2.node_name} {n3.node_name}"
        assert actual == expected[i]

def test_iter_subnode_triples_nested():
    path_list = [
        "sub/rel_d2_#1/objsubj_d3_#1/rel_d4_#1/obj_d5_#1",
        "sub/rel_d2_#1/objsubj_d3_#1/rel_d4_#2/obj_d5_#2",
    ]
    expected = [
        "sub1 rel1 obj11",
        "sub1 rel1 obj12",
        "sub1 rel2 obj21",
    ]
    root = list_to_tree(path_list)
    print_tree(root)
    for i, (n1, n2, n3) in enumerate(iter_subnode_triples(root)):
        actual = f"{n1.node_name} {n2.node_name} {n3.node_name}"
        print(actual)
        # assert actual == expected[i]

def test_iter_subnode_triples_depths():
    examples = [
        ["sub1/rel1/obj1"],
        ["r1/sub1/rel1/obj1"],
        ["r1/r2/sub1/rel1/obj1"],
    ]

    for exnum, example in enumerate(examples):
        root = list_to_tree(example)
        desc = get_nth_descendent(root, exnum)
        assert desc is not None
        for n1, n2, n3 in iter_subnode_triples(desc):
            assert n1.node_name == "sub1"
            assert n2.node_name == "rel1"
            assert n3.node_name == "obj1"
