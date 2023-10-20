import typing as t

from bigtree.node.node import Node
from dblp_service.lib.predef.log import create_logger
from dblp_service.rdf_io.tree_traverse_handlers import (
    AuthorshipPropertyHandlers,
)
from dblp_service.rdf_io.dblp_repr import (
    KeyValProp,
    DblpRepr,
    Publication,
)

from dblp_service.rdf_io.trees import iter_subject_triples, simplify_urlname

log = create_logger(__file__)


def get_isA_handler(
    node: Node, handlers: AuthorshipPropertyHandlers
) -> t.Optional[t.Callable[[Node, Node], t.Optional[DblpRepr]]]:
    rel = simplify_urlname(node.node_name)
    handler = f"isA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func


def get_hasA_handler(
    node: Node, handlers: AuthorshipPropertyHandlers
) -> t.Optional[t.Callable[[Node, Node], t.Optional[DblpRepr]]]:
    rel = simplify_urlname(node.node_name)
    handler = f"hasA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func


def traverse_authorship_tree(root: Node) -> DblpRepr:
    handlers = AuthorshipPropertyHandlers()

    ## First time through, handle the 'isA' properties
    for nsubj, nrel, nobj in iter_subject_triples(root):
        if nrel.node_name != "isA":
            continue

        func = get_isA_handler(nobj, handlers)
        if func:
            created = func(nsubj, nobj)
            if created:
                log.info(f"created isA {created}")
                nsubj.set_attrs(dict(entry=created))

    ## Second time through, handle the 'hasA' properties
    for nsubj, nrel, nobj in iter_subject_triples(root):
        if nrel.node_name == "isA":
            continue

        func = get_hasA_handler(nrel, handlers)
        if func:
            prior = nsubj.get_attr("entry")
            if prior is None:
                continue
            # assert prior is not None
            created = func(nrel, nobj)
            if created:
                log.info(f"hasA {created}")
                combined = prior.merge(created)
                log.info(f"  == {combined}")
                nsubj.set_attrs(dict(entry=combined))

    root_entry = root.get_attr("entry")

    assert root_entry is not None
    return root_entry


def has_prop(pub: Publication, prop: KeyValProp) -> bool:
    def is_match(pub_prop: KeyValProp) -> bool:
        return pub_prop.key == prop.key

    matched_props = list(filter(is_match, pub.props))
    return len(matched_props) > 0


def get_prop(pub: Publication, prop_key: str) -> t.Optional[KeyValProp]:
    def is_match(pub_prop: KeyValProp) -> bool:
        return pub_prop.key == prop_key

    matched_props = list(filter(is_match, pub.props))
    if len(matched_props) == 0:
        return None
    return matched_props[0]


def authorship_tree_to_repr(root: Node) -> t.List[DblpRepr]:
    """ """
    return [traverse_authorship_tree(subject) for subject in root.children]
