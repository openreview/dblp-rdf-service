from collections import defaultdict
import typing as t
from bigtree.node.node import Node
from bigtree.tree.search import find_child
import re


# Tree = t.Dict[str, t.Optional["Tree"]]
Tree = Node


def node():
    return defaultdict(node)


def tree_get(tree: Tree, path: t.List[str]) -> t.Optional[str]:
    pass
    # node: Tree = tree
    # for p in path:
    #     v = node.get(p)
    #     if not v:
    #         return
    #     node = v


def tree_get_str(tree: Tree, path: t.List[str]) -> t.Optional[str]:
    if not path:
        if len(tree.children) == 0:
            return None

        value = tree.children[0].node_name
        return value

    path0 = path[0]

    def match_node(n: Node) -> bool:
        return n.node_name.endswith(path0)

    child = find_child(tree, match_node)
    if not child:
        return None
    return tree_get_str(child, path[1:])


def tree_get_tree(tree: Tree, path: t.List[str]) -> t.Optional[Tree]:
    pass


def tree_path_exists(tree: Tree, path: t.List[str]) -> bool:
    return False
