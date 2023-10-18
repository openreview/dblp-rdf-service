from dataclasses import replace
import typing as t

from bigtree.node.node import Node
from dblp_service.rdf_io.tree_traverse_handlers import (
    AuthorshipPropertyHandlers,
    KeyValProp,
    NameList,
    NameSpec,
    OutputBase,
    Publication,
)

from dblp_service.rdf_io.trees import iter_subject_triples, simplify_urlname


def isA_handler(
    node: Node, handlers: AuthorshipPropertyHandlers
) -> t.Optional[t.Callable[[Node, Node], t.Optional[OutputBase]]]:
    rel = simplify_urlname(node.node_name)
    handler = f"isA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func


def hasA_handler(
    node: Node, handlers: AuthorshipPropertyHandlers
) -> t.Optional[t.Callable[[Node, Node], t.Optional[OutputBase]]]:
    rel = simplify_urlname(node.node_name)
    handler = f"hasA_{rel}"
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        return func


def apply_handlers_to_tree(root: Node) -> OutputBase:
    handlers = AuthorshipPropertyHandlers()

    ## First time through, handle the 'isA' properties
    for nsubj, nrel, nobj in iter_subject_triples(root):
        if nrel.node_name != "isA":
            continue

        func = isA_handler(nobj, handlers)
        if func:
            created = func(nsubj, nobj)
            if created:
                nsubj.set_attrs(dict(entry=created))

    ## Second time through, handle the 'hasA' properties
    for nsubj, nrel, nobj in iter_subject_triples(root):
        if nrel.node_name == "isA":
            continue

        func = hasA_handler(nrel, handlers)
        if func:
            prior = nsubj.get_attr("entry")
            if prior is None:
                continue
            # assert prior is not None
            created = func(nrel, nobj)
            if created:
                combined = combine_outputs(prior, created)
                nsubj.set_attrs(dict(entry=combined))

    root_entry = root.get_attr("entry")

    assert root_entry is not None
    return root_entry


def combine_outputs(o1: OutputBase, o2: OutputBase) -> OutputBase:
    if isinstance(o1, NameSpec):
        if isinstance(o2, NameSpec):
            return NameSpec(
                name_type=o1.name_type if o1.name_type is not None else o2.name_type,
                fullname=o1.fullname if o1.fullname is not None else o2.fullname,
                ordinal=o1.ordinal if o1.ordinal is not None else o2.ordinal,
            )

    elif isinstance(o1, NameList):
        if isinstance(o2, NameSpec):
            names = o1.names
            names.append(o2)
            return replace(o1, names=names)

    elif isinstance(o1, Publication):
        if isinstance(o2, NameSpec):

            def is_match(p: KeyValProp):
                return o2.name_type == p.key

            matched_props = list(filter(is_match, o1.props))
            if not matched_props:
                name_type = o2.name_type
                assert name_type is not None
                name_list = NameList(name_type, [o2])
                prop = KeyValProp(key=name_type, value=name_list)
                return replace(o1, props=[prop])
            else:
                assert len(matched_props) == 1
                prop = matched_props[0]
                name_list = prop.value
                if isinstance(name_list, NameList):
                    new_name_list = combine_outputs(name_list, o2)
                    o1.props.remove(prop)
                    new_prop = replace(prop, value=new_name_list)
                    return replace(o1, props=o1.props + [new_prop])
        elif isinstance(o2, KeyValProp):
            return replace(o1, props=o1.props + [o2])

    raise Exception("no suitable combination")
