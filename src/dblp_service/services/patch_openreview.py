"""Fill in missing openreview publication data.

"""

import typing as t

from dblp_service.lib.config import Config
from dblp_service.lib.filesys import ensure_directory
from dblp_service.lib.log import AppLogger, create_logger
from dblp_service.local_storage.fuseki_context import FusekiServerManager
from dblp_service.local_storage.graph_naming import GraphName, uri_to_graph_name

DblpPubID = t.NewType('DblpPubID', str)
DblpAuthID = t.NewType('DblpAuthID', str)

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
class OpenreviewUpdateService:
    log: AppLogger

    def __init__(self):
        self.log = create_logger(self.__class__.__name__)

    def fetch_publication_authors(self, pub_id: DblpPubID) -> t.List[DblpAuthID]:
        return []

    def update_publication(self, pub_id: DblpPubID):
        """"""
        auth_ids = self.fetch_publication_authors(pub_id)
        for auth_id in auth_ids:
            self.align_author(auth_id)


    def align_author(self, auth_id: DblpAuthID):
        """"""

    def fetch_or_author(self, auth_id: DblpAuthID, pub_id: DblpPubID):
        """"""


class PublicationAlignment:
    pass
