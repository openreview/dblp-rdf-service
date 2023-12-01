"""Fill in missing openreview publication data.

"""

import dataclasses as dc
from functools import reduce
from pprint import pprint
import re
import typing as t

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
import operator as op


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
    return r.get('key', '<?>')


def repr_title(r: DblpRepr) -> str:
    return r.get('title', '<?>')


def print_aligned(aligned: Alignments):
    table = Table(show_edge=False, show_footer=False)
    table.add_column('Key', header_style='bold')
    table.add_column('OpenReview', header_style='blue bold')
    table.add_column('dblp.org', header_style='green bold')
    table.add_column('title')

    pprint(aligned)
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


def align_pubs(notes: t.List[Note], reprs: t.List[DblpRepr]) -> Alignments:
    """Match OpenReview Notes to dblp.org publications.

    For each publication  (notes and dblp), generate a list  of keys which which
    can be  used to match papers  across the two domains.  Possible keys include
    e.g., dblp pids, DOIs, arXiv ids, and normalized title words.

    """
    # generate pubkey pairs
    #   (pubkey -> note),
    #   (pubkey -> dblp)
    note_key_pairs = [(pubkey, note) for note in notes for pubkey in gen_note_key(note)]
    dblp_key_pairs = [(pubkey, repr) for repr in reprs for pubkey in gen_dblp_key(repr)]

    # Collapse note pairs into multimap
    #    { pubkey : [note, ...] }
    note_mmap: t.Dict[PubKey, t.List[Note]] = pairs_to_multimap(note_key_pairs)

    # Collapse dblp pairs into multimap
    #    { pubkey : [dblp, ...] }
    dblp_mmap: t.Dict[PubKey, t.List[DblpRepr]] = pairs_to_multimap(dblp_key_pairs)

    # Warn if multiple values in multimaps
    #   Multiple values means that either:
    #      - the pubkey does not uniquely identify a single paper
    #      - OpenReview queries are returning the same paper multiple times
    #      - dblp.org rdf queries are returning the same paper multiple times
    warnings = [
        Warning(f'Multiple dblp records produced the same key {k}', [repr_key(v) for v in vs])
        for (k, vs) in dblp_mmap.items()
        if len(vs) > 1
    ]

    warnings.extend(
        [
            Warning(f'Multiple notes produced the same key {k}', [v.id for v in vs])
            for (k, vs) in note_mmap.items()
            if len(vs) > 1
        ]
    )

    # Reduce the multimaps to 1-to-1 mono-maps
    #     { pubkey: note }
    #     { pubkey: dblp }
    note_monomap: t.Dict[PubKey, Note] = {k: vs[0] for (k, vs) in note_mmap.items()}
    dblp_monomap: t.Dict[PubKey, DblpRepr] = {k: vs[0] for (k, vs) in dblp_mmap.items()}

    # Create a list of relations of the shape:
    #    note -> [pubkey1, pubkey2, ...]  -> dblp
    #
    # Represent relations as a multimap with a compound key:
    #       { (note_id, dblp_id) : [pubkey, ...] }

    # Create a list of ids -> pubkey
    compound_key_pairs: t.List[t.Tuple[t.Tuple[str, str], PubKey]] = []
    for pubkey, note in note_monomap.items():
        dblp_id = repr_key(dblp_monomap[pubkey]) if pubkey in dblp_monomap else ''
        compound_key_pairs.append(((note.id, dblp_id), pubkey))

    for pubkey, repr in dblp_monomap.items():
        note_id = note_monomap[pubkey].id if pubkey in note_monomap else ''
        repr_id = repr_key(repr)
        compound_key_pairs.append(((note_id, repr_id), pubkey))

    # This map contains all edges between note -> dblp publications
    compound_key_mmap = pairs_to_multimap(compound_key_pairs)

    compound_keys = set(compound_key_mmap.keys())
    unmatched_note_keys = set([note_pubkey for note_pubkey, dblp_pubkey in compound_keys if not dblp_pubkey])
    # [(noteid, dblpid) for ((noteid, dblpid), v) in compound_key_mmap.values()]

    # Determine all matched/unmatched relations between notes/dblps
    unmatched_notes = set([note_id for note_id, dblp_id in compound_keys if not dblp_id])
    unmatched_dblps = set([dblp_id for note_id, dblp_id in compound_keys if not note_id])
    matched_pubsets = [{note_id, dblp_id} for note_id, dblp_id in compound_keys if note_id and dblp_id]
    matched_pubs: t.Set[str] = reduce(op.or_, matched_pubsets, set())

    alignments = Alignments(
        note_map=note_monomap,
        dblp_map=dblp_monomap,
        unmatched_notes=unmatched_notes,
        unmatched_dblps=unmatched_dblps,
        matched_pubs=matched_pubs,
        warnings=warnings,
    )

    return alignments


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


# unmatched_notes: t.Set[PubKey] = note_keys - dblp_keys
# unmatched_dblps: t.Set[PubKey] = dblp_keys - note_keys
# matched_pubs: t.Set[PubKey] = dblp_keys & note_keys
# all_keys: t.Set[PubKey] = dblp_keys | note_keys
# edges: t.Set[t.Tuple[str, int, str, int]] = set()

# for key in all_keys:
#     ns = note_mmap.get(key, [])
#     ds = dblp_mmap.get(key, [])
#     if not ns:
#         pass
#     elif not ds:
#         pass
#     else:
#         pass
#     keyed_edges = [(n.id, i, repr_key(d), j) for i, n in enumerate(ns) for j, d in enumerate(ds)]
#     edges.update(keyed_edges)

# cats = AlignmentCategories()
# for edge in edges:
#     match edge:
#         case (note_id, 0, repr_id, 0):
#             # cats.shared.append(apubs)
#             pass
#         case (note_id, note_num, repr_id, repr_num):
#             pass
#     pass

# aligned: t.Dict[PubKey, MatchedPubs] = {}
# aldict = AlignmentDict()
# for note in notes:
#     for key in gen_note_key(note):
#         prev = aligned.setdefault(key, MatchedPubs(key))
#         combined = prev.notes | dict([(note.id, note)])
#         updated = dc.replace(prev, notes=combined)
#         aligned[key] = updated
#         aldict.notes.setdefault(note.id, []).append(updated)

# for repr in reprs:
#     for key in gen_dblp_key(repr):
#         prev = aligned.setdefault(key, MatchedPubs(key))
#         combined_reprs = prev.reprs | dict([(repr_key(repr), repr)])
#         updated = dc.replace(prev, reprs=combined_reprs)
#         aligned[key] = updated
#         aldict.reprs.setdefault(repr_key(repr), []).append(updated)

# return separate_aligned(aligned), aldict

# def separate_aligned(aligned: t.Dict[PubKey, MatchedPubs]) -> AlignmentCategories:
#     cats = AlignmentCategories()
#     for k, apubs in aligned.items():
#         nreprs, nnotes = len(apubs.reprs), len(apubs.notes)
#         if nreprs == 1 and nnotes == 1:
#             cats.shared.append(apubs)
#         elif nreprs == 0 and nnotes == 1:
#             cats.only_openreview.append(apubs)
#         elif nreprs == 1 and nnotes == 0:
#             cats.only_dblp.append(apubs)
#         else:
#             cats.spurious.append(apubs)

#     return cats

# def print_aligned(cats: AlignmentCategories):
#     table = Table(show_edge=False, show_footer=False)
#     table.add_column('Key', header_style='bold')
#     table.add_column('OpenReview', header_style='blue bold')
#     table.add_column('dblp.org', header_style='green bold')
#     table.add_column('title')

#     for apub in cats.shared:
#         assert len(apub.notes) > 0
#         assert len(apub.reprs) > 0
#         key = str(apub.pubkey)
#         note0 = list(apub.notes.values())[0]
#         title = note0.content.title
#         table.add_row(key, 'Y', 'Y', title)

#     for apub in cats.only_openreview:
#         assert len(apub.reprs) == 0
#         key = str(apub.pubkey)
#         note0 = list(apub.notes.values())[0]
#         title = note0.content.title
#         table.add_row(key, 'Y', 'N', title)

#     for apub in cats.only_dblp:
#         assert len(apub.notes) == 0
#         key = str(apub.pubkey)
#         repr0 = list(apub.reprs.values())[0]
#         title = repr_title(repr0)
#         table.add_row(key, 'N', 'Y', title)

#     for apub in cats.spurious:
#         key = str(apub.pubkey)
#         note0 = list(apub.notes.values())[0]
#         title = note0.content.title
#         table.add_row(key, '?', '?', title)

#     console = Console()
#     console.print(table)

# @dc.dataclass
# class MatchedPubs:
#     """Record of all publications that match the given key"""

#     pubkey: PubKey
#     notes: t.Dict[str, Note] = dc.field(default_factory=dict)
#     reprs: t.Dict[str, DblpRepr] = dc.field(default_factory=dict)


# @dc.dataclass
# class AlignmentCategories:
#     shared: t.List[MatchedPubs] = dc.field(default_factory=list)
#     only_openreview: t.List[MatchedPubs] = dc.field(default_factory=list)
#     only_dblp: t.List[MatchedPubs] = dc.field(default_factory=list)
#     spurious: t.List[MatchedPubs] = dc.field(default_factory=list)

# @dc.dataclass
# class AlignmentDict:
#     notes: t.Dict[str, t.List[MatchedPubs]] = dc.field(default_factory=dict)
#     reprs: t.Dict[str, t.List[MatchedPubs]] = dc.field(default_factory=dict)
