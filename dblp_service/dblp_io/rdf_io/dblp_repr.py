"""Intermediate repr classes for DBLP authored works.

"""

from abc import ABC, abstractmethod
from dataclasses import astuple, dataclass, field, replace, KW_ONLY
import typing as t
from bigtree.node.node import Node


@dataclass
class DblpRepr(ABC):
    @abstractmethod
    def merge(self, other: "DblpRepr") -> "DblpRepr":
        pass


def merge_tuplewise(r1: DblpRepr, r2: DblpRepr) -> t.List[t.Any]:
    fields = list(zip(astuple(r1), astuple(r2)))
    merged: t.List[t.Any] = []

    for f1, f2 in fields:
        match (f1, f2):
            case (str(s1), str(s2)):
                merged.append(s1 if s1 else s2)
            case ([*l1elems], [*l2elems]):
                merged.append(l1elems + l2elems)
            case (int(i1), int(i2)):
                merged.append(i1 if i1 else i2)
            case _:
                raise Exception(f"merge_tuplewise: unmergable {f1} / {f2}")

    return merged



@dataclass
class NameSpec(DblpRepr):
    name_type: str = ""
    fullname: str = ""
    ordinal: int = 0

    def merge(self, other: DblpRepr) -> DblpRepr:
        if isinstance(other, NameSpec):
            return NameSpec(*merge_tuplewise(self, other))

        raise Exception(f"no suitable combination {self.__class__} / {other.__class__}")

    def __repr__(self) -> str:
        t = self.name_type or "??"
        n = self.fullname or "<noname>"
        return f"{t}:{n}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class ResourceIdentifier(DblpRepr):
    id_scheme: str = ""  # dblp-record | doi
    value: str = ""

    def merge(self, other: DblpRepr) -> DblpRepr:
        if isinstance(other, ResourceIdentifier):
            return ResourceIdentifier(*merge_tuplewise(self, other))

        raise Exception(f"no suitable combination {self.__class__} / {other.__class__}")

    def __repr__(self) -> str:
        t = self.id_scheme or "_"
        n = self.value or "_"
        return f"ResourceID={t}:{n}"


@dataclass
class KeyValProp(DblpRepr):
    key: str
    value: t.Union[str, t.List[NameSpec]]

    def merge(self, other: DblpRepr) -> DblpRepr:
        if isinstance(other, KeyValProp):
            assert self.key == other.key
            if isinstance(self.value, str) and isinstance(other.value, str):
                return KeyValProp(self.key, self.value + other.value)

            assert isinstance(self.value, t.List) and isinstance(other.value, t.List)
            return KeyValProp(self.key, self.value + other.value)

        raise Exception(f"no suitable combination {self.__class__} / {other.__class__}")

    def __repr__(self) -> str:
        return f"{self.key}: {self.value}"

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class Publication(DblpRepr):
    pub_type: str = ""
    key: str = ""
    schema: str = ""
    props: t.List[KeyValProp] = field(default_factory=list)
    propd: t.Dict[str, KeyValProp] = field(default_factory=dict)

    def merge(self, other: DblpRepr) -> DblpRepr:
        match other:
            case NameSpec():

                def update(prop: KeyValProp) -> KeyValProp:
                    match prop:
                        case KeyValProp(str(key), value=[*elems]):
                            return KeyValProp(key, elems + [other])

                return update_prop_default(
                    self,
                    other.name_type,
                    update,
                    KeyValProp(other.name_type, [other])
                )


            case KeyValProp():
                if has_prop(self, other):
                    return self
                return replace(self, props=self.props + [other])

            case ResourceIdentifier():
                return replace(self, key=other.value, schema=other.id_scheme)

            case Publication():
                if self.pub_type == "Publication":
                    return Publication(*merge_tuplewise(other, self))
                else:
                    return Publication(*merge_tuplewise(self, other))

            case _:
                raise Exception(f"no suitable combination {self.__class__} / {other.__class__}")

    def __repr__(self) -> str:
        ps = [str(p) for p in self.props]
        return f"@{self.pub_type}({self.key}){ps}"

    def __str__(self) -> str:
        return self.__repr__()


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


# def create_or_update_prop(maybe_prop: t.Optional[KeyValProp]) -> KeyValProp:
#     match maybe_prop:
#         case None:
#             return KeyValProp(other.name_type, [other])
#         case KeyValProp(str(key), value=[*elems]):
#             return KeyValProp(key, elems + [other])


def update_prop(pub: Publication, prop_key: str, f: t.Callable[[t.Optional[KeyValProp]], KeyValProp]) -> Publication:
    updated: t.List[KeyValProp] = []
    for prop in pub.props:
        if prop.key == prop_key:
            updated.append(f(prop))
        else:
            updated.append(prop)
    return replace(pub, props=updated)


def update_prop_default(
    pub: Publication, prop_key: str, f: t.Callable[[KeyValProp], KeyValProp], fallback: KeyValProp
) -> Publication:
    updated: t.List[KeyValProp] = []
    found_key = False
    for prop in pub.props:
        if prop.key == prop_key:
            updated.append(f(prop))
            found_key = True
        else:
            updated.append(fallback)
    if not found_key:
        updated.append(fallback)

    return replace(pub, props=updated)

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
class EmitRepr(UpdateOperation):
    target: Node
    value: t.Any


HandlerType = t.Callable[[Node, Node], t.Optional[UpdateOperation]]
