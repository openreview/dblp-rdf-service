"""Intermediate repr classes for DBLP authored works.

"""

from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from dataclasses import dataclass, KW_ONLY
import typing as t
from bigtree.node.node import Node
import collections as col


P = t.ParamSpec("P")

# class DblpRepr(MutableMapping[str, t.Any]):
class DblpRepr(col.UserDict[str, t.Any]):
    # data: t.Dict[str, t.Any] = dict()

    def __init__(self, **kwargs: str):
        super().__init__(**kwargs)
        # self.data |= dict(kwargs)

    @abstractmethod
    def fieldnames(self) -> t.List[str]:
        pass

    # def __missing__(self, key: str) -> t.Any:
    #     raise KeyError(key)

    # def __contains__(self, key: object) -> bool:
    #     return key in self.data

    # def __setitem__(self, key: str, item: t.Any):
    #     self.data[key] = item

    # def __getitem__(self, key: str):
    #     return self.data[key]

    # def __delitem__(self, key: str):
    #     del self.data[key]

    # def __len__(self):
    #     return len(self.data)

    # def __iter__(self):
    #     return iter(self.data)

    # def __repr__(self):
    #     return self.data.__repr__()

    # def __str__(self):
    #     return self.data.__str__()

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
class AppendField(UpdateOperation):
    field: str
    value: t.Any

@dataclass
class EmitRepr(UpdateOperation):
    target: Node
    value: DblpRepr


HandlerType: t.TypeAlias = t.Callable[[Node, Node], t.Optional[UpdateOperation]]
