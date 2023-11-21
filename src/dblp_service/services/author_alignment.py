"""Fill in missing openreview publication data.

"""

from dataclasses import asdict
from pprint import pprint
import typing as t
from dblp_service.lib.log import AppLogger, create_logger
from dblp_service.open_exchange.open_fetch import fetch_notes_for_author, fetch_profile, fetch_profile_with_dblp_pid
from os import path

DblpPubID = t.NewType('DblpPubID', str)
DblpAuthID = t.NewType('DblpAuthID', str)
OpenRAuthID = t.NewType('OpenRAuthID', str)

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
    def fetch_profile(self, auth_id: t.Union[OpenRAuthID, DblpAuthID]):
        dblp_uri = path.join('https://dblp.org/pid', auth_id)
        fetch_profile_with_dblp_pid(dblp_uri)
        # match auth_id:
        #     case OpenRAuthID():
        #         pass
        #     case DblpAuthID():
        #         dblp_uri = path.join('https://dblp.org/pid', auth_id)
        #         fetch_profile_with_dblp_pid(dblp_uri)

    def fetch_author_publications(self, auth_id: OpenRAuthID):
        return fetch_notes_for_author(auth_id)


class DblpOrgFetcher:
    def fetch_publication_authors(self, pub_id: DblpPubID) -> t.List[DblpAuthID]:
        return []


class AuthorPublicationAlignment:
    log: AppLogger
    openr_fetch: OpenreviewFetcher
    dblp_org_fetch: DblpOrgFetcher

    def __init__(self):
        self.log = create_logger(self.__class__.__name__)
        self.openr_fetch = OpenreviewFetcher()
        self.dblp_org_fetch = DblpOrgFetcher()

    def align_author(self, auth_id: DblpAuthID):
        self.openr_fetch.fetch_profile(auth_id)
        # fetch author w/content.dblp == 'https://dblp.org/{auth_id}'
        # self.openr_fetch.fetch_author_profile
        pass


def align_authorship():
    profile = fetch_profile(id)
    if profile:
        pprint(asdict(profile))
        print('Notes==================')
        for note in fetch_notes_for_author(id):
            pprint(asdict(note))

    else:
        print('No Profile found')
