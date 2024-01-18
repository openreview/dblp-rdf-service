import dataclasses as dc
import typing as t
from icecream import ic  # type: ignore
from os import path
from dblp_service.open_exchange.note_schemas import Note
from dblp_service.pub_formats.rdf_tuples.dblp_repr import DblpRepr


@dc.dataclass
class DblpPubID:
    id: str


@dc.dataclass
class DblpAuthID:
    http_prefix = 'https://dblp.org/'
    _pid: str

    def __init__(self, s: str) -> None:
        ic(s)
        segments = [s for s in s.split('/') if len(s) > 0]
        ic(segments)
        if s.startswith(self.http_prefix):
            suffix = s[len(self.http_prefix) :]
            segments = [s for s in suffix.split('/') if len(s) > 0]
        ic(segments)
        match segments:
            case ['pid', id1, id2]:
                self._pid = path.join(id1, id2)
                return
            case [id1, id2]:
                self._pid = path.join(id1, id2)
                return
            case _:
                pass
        raise Exception(f'invalid dblp pid: {s}')

    def pid(self) -> str:
        return self._pid

    def uri(self) -> str:
        return path.join(self.http_prefix, 'pid', self._pid)


@dc.dataclass
class OpenRevAuthID:
    id: str


@dc.dataclass(frozen=True)
class PubKey:
    """Key derived from a publication used to match to other papers

    Fields:
        keytype : description of key e.g., title, dblp_key, doi, etc.
        value : the derived key
    """

    keytype: str
    value: str


@dc.dataclass
class AlignmentWarning:
    msg: str
    ids: t.List[str]

@dc.dataclass
class DuplicateKeyWarning:
    msg: str
    ids: t.List[str]


@dc.dataclass
class Alignments:
    note_map: t.Dict[PubKey, Note]
    dblp_map: t.Dict[PubKey, DblpRepr]
    matched_pubs: t.Set[PubKey]
    unmatched_notes: t.Set[PubKey]
    unmatched_dblps: t.Set[PubKey]
    warnings: t.List[AlignmentWarning]


@dc.dataclass
class AlignedAuthorship:
    open_auth_id: OpenRevAuthID
    dblp_auth_id: DblpAuthID
    alignments: Alignments
