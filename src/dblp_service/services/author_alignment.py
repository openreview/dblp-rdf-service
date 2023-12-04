"""Fill in missing openreview publication data.

"""

import dataclasses as dc
import re
import typing as t

from disjoint_set import DisjointSet

from rich.table import Table
from rich.console import Console

from dblp_service.lib.log import AppLogger, create_logger
from dblp_service.lib.utils import pairs_to_multimap
from dblp_service.open_exchange.note_schemas import Note
from dblp_service.open_exchange.open_fetch import fetch_notes_for_author, fetch_profile_with_dblp_pid
from os import path

from dblp_service.open_exchange.profile_schemas import Profile
from dblp_service.pub_formats.rdf_tuples.dblp_repr import DblpRepr
from dblp_service.pub_formats.rdf_tuples.queries import get_author_publication_tree
from dblp_service.pub_formats.rdf_tuples.tree_traversal import all_authorship_trees_to_reprs

from icecream import ic  # type: ignore
import functools as ft


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


class OpenreviewFetcher:
    def fetch_profile(self, auth_id: t.Union[OpenRevAuthID, DblpAuthID]) -> t.Optional[Profile]:
        print(f'matching { auth_id }')
        match auth_id:
            case OpenRevAuthID():
                pass

            case DblpAuthID() as pid:
                print(f'fetching profile { pid.uri() }')
                return fetch_profile_with_dblp_pid(pid.uri())

        return None

    def fetch_author_publications(self, auth_id: OpenRevAuthID) -> t.List[Note]:
        return list(fetch_notes_for_author(auth_id.id))


class DblpOrgFetcher:
    def fetch_author_publications(self, authorid: DblpAuthID) -> t.List[DblpRepr]:
        tree = get_author_publication_tree(authorid.uri())
        dblp_papers = all_authorship_trees_to_reprs(tree, step_debug=False)

        def get_title(repr: DblpRepr) -> str:
            return repr.get('title', '<no title>')

        dblp_papers.sort(key=get_title)
        return dblp_papers


class AuthorPublicationAlignment:
    log: AppLogger
    openr_fetch: OpenreviewFetcher
    dblp_org_fetch: DblpOrgFetcher

    def __init__(self):
        self.log = create_logger(self.__class__.__name__)
        self.openr_fetch = OpenreviewFetcher()
        self.dblp_org_fetch = DblpOrgFetcher()

    def align_author(self, authorid: DblpAuthID):
        profile = self.openr_fetch.fetch_profile(authorid)
        if not profile:
            self.log.info(f'No profile found for author, {authorid}')
            return

        openrev_auth_id = OpenRevAuthID(profile.id)
        openreview_pubs = self.openr_fetch.fetch_author_publications(openrev_auth_id)

        def get_pub_title(note: Note) -> str:
            return note.content.title

        openreview_pubs.sort(key=get_pub_title)

        ## Create keys for OpenReview notes
        for note in openreview_pubs:
            # title match
            note.content.title
            # doi from html
            note.content.html
            # dblp pid or doi from bibtex
            note.content._bibtex

        dblp_papers = self.dblp_org_fetch.fetch_author_publications(authorid)

        aligned_pub_table = Table(show_edge=False, show_footer=False)
        aligned_pub_table.add_column('OpenReview', header_style='green bold')
        aligned_pub_table.add_column('https://dblp.org', header_style='green bold')

        max_len = max(len(dblp_papers), len(openreview_pubs))
        for i in range(max_len):
            pub_title = openreview_pubs[i].content.title if i < len(openreview_pubs) else 'no more'
            dblp_title = dblp_papers[i].get('title', '<no title>') if i < len(dblp_papers) else 'all done'
            aligned_pub_table.add_row(pub_title, dblp_title)

        console = Console()
        console.print(aligned_pub_table)


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
class Warning:
    msg: str
    ids: t.List[str]


@dc.dataclass
class Alignments:
    note_map: t.Dict[PubKey, Note]
    dblp_map: t.Dict[PubKey, DblpRepr]
    matched_pubs: t.Set[PubKey]
    unmatched_notes: t.Set[PubKey]
    unmatched_dblps: t.Set[PubKey]
    warnings: t.List[Warning]


def repr_key(r: DblpRepr) -> str:
    return r.get('key', '<?>')  # TODO will this <?> cause keys to falsely merge?


def repr_title(r: DblpRepr) -> str:
    return r.get('title', '<?>')


def normalize_title_str(title: str) -> str:
    t = re.sub(r'\s+', '_', title.lower())
    t = re.sub(r'[^\w\d]', '', t)
    return t


def gen_dblp_key(pub: DblpRepr) -> t.List[PubKey]:
    keys: t.List[PubKey] = []
    if key := pub.get('key'):
        keys.append(PubKey('dblp_key', key))

    if key := pub.get('title'):
        key = normalize_title_str(key)
        keys.append(PubKey('title', key))

    return keys


def gen_note_key(note: Note) -> t.List[PubKey]:
    keys: t.List[PubKey] = []
    if bibtex := note.content._bibtex:
        dblp_key_re = re.compile('(DBLP:[^,]+),')
        for keymatch in dblp_key_re.finditer(bibtex):
            g1 = keymatch.group(1)
            keys.append(PubKey('dblp_key', g1))

    title = note.content.title
    title = normalize_title_str(title)
    keys.append(PubKey('title', title))
    ## TODO: keys based on: doi, arxiv.org link

    return keys


def print_aligned(aligned: Alignments):
    table = Table(show_edge=False, show_footer=False)
    table.add_column('Key', header_style='bold')
    table.add_column('OpenReview', header_style='blue bold')
    table.add_column('dblp.org', header_style='green bold')
    table.add_column('title')

    for key in aligned.matched_pubs:
        ic(key)
        note, dblp = aligned.note_map[key], aligned.dblp_map[key]
        title = note.content.title
        table.add_row(str(key), 'Y', 'Y', title)

    for key in aligned.unmatched_notes:
        note = aligned.note_map[key]
        title = note.content.title
        table.add_row(str(key), 'Y', 'N', title)

    for key in aligned.unmatched_dblps:
        dblp = aligned.dblp_map[key]
        title = repr_title(dblp)
        table.add_row(str(key), 'N', 'Y', title)

    console = Console()
    console.print(table)
    for w in aligned.warnings:
        console.print(w)


def disjoint_add(ds: DisjointSet[PubKey], pubkeys: t.List[PubKey]):
    if not pubkeys:
        return
    k0 = pubkeys[0]
    ds.find(k0)
    for k in pubkeys[1:]:
        ds.union(k0, k)


def disjoint_canonical(ds: DisjointSet[PubKey], pk: PubKey):
    """Add key and return canonical element."""
    return ds.find(pk)


def align_publications(notes: t.List[Note], reprs: t.List[DblpRepr]) -> Alignments:
    pubkey_sets: DisjointSet[PubKey] = DisjointSet()
    add_keys = ft.partial(disjoint_add, pubkey_sets)
    canonical_key = ft.partial(disjoint_canonical, pubkey_sets)

    #  Note      |   Dblp
    #  [k1, k2]  |  [k2, k5]
    note_pubkeys = [(gen_note_key(note), note) for note in notes]
    for pkeys, _ in note_pubkeys:
        add_keys(pkeys)

    dblp_pubkeys = [(gen_dblp_key(repr), repr) for repr in reprs]
    for pkeys, _ in dblp_pubkeys:
        add_keys(pkeys)

    canonical_note_pubkeys = [(canonical_key(keys[0]), pub) for (keys, pub) in note_pubkeys if keys]
    warnings: t.List[Warning] = []
    note_mmap = pairs_to_multimap(canonical_note_pubkeys)
    warnings.extend(
        [
            Warning(f'Multiple notes produced the same key {k}', [v.id for v in vs])
            for (k, vs) in note_mmap.items()
            if len(vs) > 1
        ]
    )

    canonical_dblp_pubkeys = [(canonical_key(keys[0]), pub) for (keys, pub) in dblp_pubkeys if keys]
    dblp_mmap = pairs_to_multimap(canonical_dblp_pubkeys)
    warnings.extend(
        [
            Warning(f'Multiple dblp records produced the same key {k}', [repr_key(v) for v in vs])
            for (k, vs) in dblp_mmap.items()
            if len(vs) > 1
        ]
    )

    # Reduce the multimaps to 1-to-1 mono-maps
    #     { pubkey: note }
    #     { pubkey: dblp }
    note_monomap: t.Dict[PubKey, Note] = {k: vs[0] for (k, vs) in note_mmap.items()}
    dblp_monomap: t.Dict[PubKey, DblpRepr] = {k: vs[0] for (k, vs) in dblp_mmap.items()}
    note_canonical_keys = set(note_monomap.keys())
    dblp_canonical_keys = set(dblp_monomap.keys())

    matched_pubs = note_canonical_keys & dblp_canonical_keys
    unmatched_notes = note_canonical_keys - matched_pubs
    unmatched_dblps = dblp_canonical_keys - matched_pubs

    alignments = Alignments(
        note_map=note_monomap,
        dblp_map=dblp_monomap,
        unmatched_notes=unmatched_notes,
        unmatched_dblps=unmatched_dblps,
        matched_pubs=matched_pubs,
        warnings=warnings,
    )

    return alignments


def suggest_alignment_corrections():
    """Produce a list of POST updates to OpenReview to add/update missing pub data."""
