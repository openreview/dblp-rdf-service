"""Intermediate repr classes for DBLP authored works.

"""

from abc import ABC, abstractmethod
from dataclasses import astuple, dataclass, field, replace
import typing as t


@dataclass
class DblpRepr(ABC):
    @abstractmethod
    def merge(self, other: "DblpRepr") -> "DblpRepr":
        pass


def merge_tuplewise(r1: DblpRepr, r2: DblpRepr) -> t.List[t.Any]:
    fields = list(zip(astuple(r1), astuple(r2)))

    def can_merge(s1: t.Any, s2: t.Any) -> bool:
        if isinstance(s1, str) and isinstance(s2, str):
            return len(s1) == 0 or len(s2) == 0
        if isinstance(s1, t.List) and isinstance(s2, t.List):
            return True
        if isinstance(s1, int) and isinstance(s2, int):
            return True
        return False

    # throw exception if trying to merge 2 non-empty strings
    assert all([can_merge(s1, s2) for (s1, s2) in fields])

    return [f1 + f2 for f1, f2 in fields]


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


    def merge(self, other: DblpRepr) -> DblpRepr:
        if isinstance(other, NameSpec):

            def update(maybe_prop: t.Optional[KeyValProp]) -> KeyValProp:
                if maybe_prop and isinstance(maybe_prop.value, t.List):
                    return replace(maybe_prop, value=maybe_prop.value + [other])
                return KeyValProp(other.name_type, [other])

            return update_prop(self, other.name_type, update)

        if isinstance(other, KeyValProp):
            if has_prop(self, other):
                return self
            return replace(self, props=self.props + [other])

        if isinstance(other, ResourceIdentifier):
            return replace(self, key=other.value, schema=other.id_scheme)

        if isinstance(other, Publication):
            pub_type = self.pub_type
            return Publication(*merge_tuplewise(self, other))

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


def update_prop(pub: Publication, prop_key: str, f: t.Callable[[t.Optional[KeyValProp]], KeyValProp]) -> Publication:
    updated: t.List[KeyValProp] = []
    for prop in pub.props:
        if prop.key == prop_key:
            updated.append(f(prop))
        else:
            updated.append(prop)
    return replace(pub, props=updated)
