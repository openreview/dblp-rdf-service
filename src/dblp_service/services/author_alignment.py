"""Fill in missing openreview publication data.

"""

import dataclasses as dc
import re
import typing as t

from rich.table import Table
from rich.console import Console

from dblp_service.lib.log import AppLogger, create_logger
from dblp_service.open_exchange.note_schemas import Note
from dblp_service.open_exchange.open_fetch import fetch_notes_for_author, fetch_profile_with_dblp_pid
from os import path

from dblp_service.open_exchange.profile_schemas import Profile
from dblp_service.pub_formats.rdf_tuples.dblp_repr import DblpRepr
from dblp_service.pub_formats.rdf_tuples.queries import get_author_publication_tree
from dblp_service.pub_formats.rdf_tuples.tree_traversal import all_authorship_trees_to_reprs

from icecream import ic  # type: ignore


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

    # @classmethod
    # def from_str(cls, s: str) -> 'DblpAuthID':
    #     segments = s.split('/')
    #     if s.startswith(cls.http_prefix):
    #         suffix = s[len(cls.http_prefix):]
    #         segments = suffix.split('/')
    #     match segments:
    #         case ['pid', id1, id2]:
    #             return cls(path.join(id1, id2))
    #         case _:
    #             pass

    #     raise Exception(f'invalid dblp pid: {s}')


@dc.dataclass
class OpenRevAuthID:
    id: str


# Linkage Table
# Authors
#     Dblp.org      | link-type           |  Openreview
#     /pid/m/Druck       explicit-id           ~Druck1
#
# Papers
#

# - Starting with dblp pub id, e.g., 'conf/acl/DruckGG11'
# - From dblp.org:
#    - Get full pub by pid
#    - Get pub authors (as dblp-authors)
#
# - From Openreview:
#    - Lookup note  by pid
#    - Lookup note authors  by pid e.g., profiles w/ content.dblp = 'https://dblp.org/pid/m/SebastianThrun'
#
#
# - foreach dblp-author
#    - if dblp-author in openreview:
#       - if dblp-pub not in openreview
#          - POST pub as note
#       - else if dblp-author not linked to dblp-pub
#          - POST linkage record
#


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
    keytype: str
    value: str


@dc.dataclass
class AlignedPubs:
    note: t.Optional[Note]
    repr: t.Optional[DblpRepr]

def print_aligned(aligned: t.Dict[PubKey, AlignedPubs]):
    for k, v in aligned.items():
        # note_title = v.note.content.title if v.note else '<none>'
        # repr_title = repr.get('title', '<none>')
        note_id = v.note.id if v.note else '<no-note>'
        repr_id = v.repr.get('key', '<repr:missing-key>') if v.repr else '<no-repr>'
        print(f'{k}: note({note_id}) repr({repr_id})')

def align_pubs(notes: t.List[Note], reprs: t.List[DblpRepr]):
    aligned: t.Dict[PubKey, AlignedPubs] = {}
    for note in notes:
        for key in openreview_pub_key(note):
            aligned[key] = AlignedPubs(note=note, repr=None)

    for repr in reprs:
        for key in dblp_pub_key(repr):
            prev = aligned.setdefault(key, AlignedPubs(note=None, repr=None))
            updated = dc.replace(prev, repr=repr)
            aligned[key] = updated

    print_aligned(aligned)


def normalize_title_str(title: str)-> str:
    t = re.sub(r'\s+', '_', title.lower())
    t = re.sub(r'[^\w\d]', '', t)
    return t

def dblp_pub_key(pub: DblpRepr) -> t.List[PubKey]:
    keys: t.List[PubKey] = []
    if key := pub.get('key'):
        keys.append(PubKey('dblp_key', key))

    if key := pub.get('title'):
        key = normalize_title_str(key)
        keys.append(PubKey('title', key))

    return keys


def openreview_pub_key(note: Note) -> t.List[PubKey]:
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
