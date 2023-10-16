"""Create a bibtex-style representation from an RDF-derived tree.
"""

import typing as t
from bigtree.node.node import Node
from bigtree.tree.export import print_tree

from dblp_service.rdf_io.tree_traverse_handlers import (
    AuthorshipPropertyHandlers,
    OutputFactory,
)

from .trees import (
    iter_subject_triples,
    simplify_relation,
)

from bibtexparser.model import (
    Entry,
    Field,
)


def get_entry(n: Node) -> t.Optional[Entry]:
    return n.get_attr("entry")


def set_entry(n: Node, entry: Entry) -> None:
    n.set_attrs(dict(entry=entry))


def has_entry(n: Node) -> bool:
    return get_entry(n) is not None


class BibTexFactory(OutputFactory[Entry]):
    def create_empty_output(self) -> Entry:
        return Entry("", "", [])

    def create_entity_class(self, entity: Node, entity_class: Node) -> Entry:
        cls = simplify_relation(entity_class.node_name)
        entry = Entry(cls, "", [])
        return entry


    def create_key_val_field(self, rel_type: Node, prop_val: Node, keystr: t.Optional[str]) -> Entry:
        name = keystr if keystr else simplify_relation(rel_type.node_name)
        value = prop_val.node_name
        entry = Entry("", "", [Field(name, value)])
        return entry

    def append_fields(self, field1: Entry, field2: Entry) -> Entry:
        entry_type = field1.entry_type + field2.entry_type
        key = field1.key + field2.key
        fields = field1.fields + field2.fields
        entry = Entry(key=key, entry_type=entry_type, fields=fields)
        return entry

    def append_child(self, field1: Entry, field2: Entry) -> Entry:
        entry_type = field1.entry_type + field2.entry_type
        key = field1.key + field2.key
        fields = field1.fields + field2.fields
        entry = Entry(key=key, entry_type=entry_type, fields=fields)
        return entry


## TODO change the generic to be Factory type
class BibTexHandlers(AuthorshipPropertyHandlers[Entry]):
    def __init__(self, factory: BibTexFactory):
        super().__init__(factory)


# class BibTexClassHandlers(AuthorshipClassHandlers):
#     def isA_Inproceedings(self, entity: Node):
#         """A conference or workshop paper."""
#         entry = Entry("inproceedings", "", [])
#         set_entry(entity, entry)


def authorship_tree_to_bibtex(root: Node):
    """ """
    for subject in root.children:
        apply_handlers_to_tree(subject)


def isA_handler(node: Node, handlers: BibTexHandlers) -> t.Optional[t.Callable[[Node, Node], t.Optional[Entry]]]:
    rel = simplify_relation(node.node_name)
    handler = f"isA_{rel}"
    print(f"looking for handler `{handler}`")
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        print(f"Found {handler}")
        return func

def hasA_handler(node: Node, handlers: BibTexHandlers) -> t.Optional[t.Callable[[Node, Node], t.Optional[Entry]]]:
    rel = simplify_relation(node.node_name)
    handler = f"hasA_{rel}"
    print(f"looking for handler `{handler}`")
    if hasattr(handlers, handler) and callable(func := getattr(handlers, handler)):
        print(f"Found {handler}")
        return func

def apply_handlers_to_tree(root: Node) -> Entry:
    handlers = BibTexHandlers(BibTexFactory())

    ## First time through, handle the 'isA' properties
    for nsubj, nrel, nobj in iter_subject_triples(root):
        if nrel.node_name != "isA":
            continue

        func = isA_handler(nobj, handlers)
        if func:
            created = func(nsubj, nobj)
            if created:
                handlers.output_factory.set_entry(nsubj, created)

    print_tree(root, all_attrs=True)

    ## Second time through, handle the 'hasA' properties
    for nsubj, nrel, nobj in iter_subject_triples(root):
        if nrel.node_name == "isA":
            continue

        func = hasA_handler(nrel, handlers)
        if func:
            prior = handlers.output_factory.get_entry(nsubj)
            print(f"hasA: prior = {nsubj.node_name}")
            assert prior is not None
            created = func(nrel, nobj)
            if created:
                appended = handlers.output_factory.append_fields(prior, created)
                handlers.output_factory.set_entry(nsubj, appended)
                print(f"Created {appended} = {prior} + {created}")
                print_tree(root, all_attrs=True)



    root_entry = get_entry(root)
    assert root_entry is not None
    return root_entry
