"""Intermediate repr classes for DBLP authored works.

"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, KW_ONLY
import typing as t
from bigtree.node.node import Node
import collections as col


class DblpRepr(col.UserDict[str, t.Any]):
    def __init__(self, **kwargs: str):
        super().__init__(**kwargs)

    @abstractmethod
    def fieldnames(self) -> t.List[str]:
        pass


class PersonName(DblpRepr):
    def __init__(self, **kwargs: str):
        super().__init__(**kwargs)

    def fieldnames(self) -> t.List[str]:
        return list("name_type fullname ordinal".split())


class ResourceIdentifier(DblpRepr):
    def __init__(self, **kwargs: str):
        super().__init__(**kwargs)

    def fieldnames(self) -> t.List[str]:
        return list("id_scheme value".split())


class Publication(DblpRepr):
    def __init__(self, **kwargs: str):
        super().__init__(**kwargs)

    def fieldnames(self) -> t.List[str]:
        return list("pub_type key schema".split())


@dataclass
class UpdateOperation(ABC):
    pass


@dataclass
class WriteReprField(UpdateOperation):
    field: str
    value: t.Any
    _: KW_ONLY
    overwrite: bool = True

@dataclass
class SetSimpleKeyValue(UpdateOperation):
    field: str
    value: t.Any
    _: KW_ONLY
    overwrite: bool = True

@dataclass
class AppendField(UpdateOperation):
    field: str
    value: t.Any


@dataclass
class EmitRepr(UpdateOperation):
    target: Node
    value: DblpRepr
    _: KW_ONLY
    replace: bool = True


HandlerType: t.TypeAlias = t.Callable[[Node, Node], t.Optional[UpdateOperation]]
