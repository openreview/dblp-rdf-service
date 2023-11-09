"""Maintain downloaded and import files in a local cache .

Stash directory structure is
- stash-root
  - downloads/
    - 3df2c/
    - ...

"""

from dataclasses import replace
import typing as t
from os import path
import os

# from dataclasses import field
from marshmallow_dataclass import dataclass
from marshmallow import Schema
import marshmallow as mm

from dblp_service.lib.predef.config import Config
from dblp_service.lib.predef.log import create_logger
from dblp_service.lib.predef.tables import format_table
from dblp_service.rdfdb.dblp_rdf_catalog import DblpOrgFileFetcher, DblpRdfCatalog, DblpRdfFile
from icecream import ic


@dataclass
class StashIndex:
    catalog: DblpRdfCatalog
    base_version: str  # md5
    head_version: str  # md5
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema

    @classmethod
    def from_catalog(cls, catalog: DblpRdfCatalog):
        latest_md5 = catalog.latest_release.md5
        previous_md5 = catalog.most_recent_archived_rdf().md5
        return cls(catalog, base_version=previous_md5, head_version=latest_md5)


class FileStash:
    root_dir: str
    downloads_dir: str
    index_file: str
    dblp_file_fetcher: DblpOrgFileFetcher

    log = create_logger("FileStash")

    def __init__(self, config: Config):
        service_root = config.dblpServiceRoot
        self.root_dir = path.join(service_root, "stash")
        self.downloads_dir = path.join(self.root_dir, "downloads")
        self.index_file = path.join(self.root_dir, "stash-index.json")
        self.dblp_file_fetcher = DblpOrgFileFetcher()

    def write_index(self, stash_index: StashIndex) -> None:
        content = StashIndex.Schema().dumps(stash_index)  # type: ignore
        with open(self.index_file, "w") as f:
            f.write(content)

    def read_index(self) -> t.Optional[StashIndex]:
        if not os.path.exists(self.index_file):
            return None

        with open(self.index_file, "r") as f:
            content = f.read()
            sindex: StashIndex = StashIndex.Schema().loads(content)  # type: ignore
            return sindex

    def ensure_dirs(self):
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)

    def update_index(self, *, old_index: StashIndex, new_index: StashIndex) -> StashIndex:
        return replace(
            new_index,
            base_version=old_index.base_version,
            head_version=old_index.head_version,
        )  # type: ignore

    def base_or_head(self, *, set_base: bool = False, set_head: bool = False) -> t.Optional[str]:
        exactly_one_set = set_base ^ set_head

        if not exactly_one_set:
            self.log.warning("Must set exactly one of set_base or set_head to True")
            return None

        return "head" if set_head else "base"

    def set_active_base_or_head_version(
        self, stash_index: StashIndex, md5: t.Optional[str], *, set_base: bool = False, set_head: bool = False
    ) -> t.Optional[StashIndex]:
        """Set the head (newer) or base (older) file version (with MD5 prefix).

        If no ID is specified,
            If set_head is True, default to latest export
            If set_base is True, default to second most recent export
        """

        if (set_which := self.base_or_head(set_base=set_base, set_head=set_head)) is None:
            self.log.error("Could not set base or head version")
            return None

        catalog = stash_index.catalog

        if not md5:
            if set_head:
                md5 = catalog.latest_release.md5
                return replace(stash_index, head_version=md5)  # type: ignore
            else:
                md5 = catalog.most_recent_archived_rdf().md5
                return replace(stash_index, base_version=md5)  # type: ignore

        md5_matches = [v.md5 for v in catalog.get_archived_releases() if v.md5.startswith(md5)]

        num_matches = len(md5_matches)

        if num_matches == 0:
            self.log.warning(f"Could not set {set_which} version; Specified MD5 not found")
            return None

        if num_matches > 1:
            self.log.warning(f"Could not set {set_which} version; Multiple matching MD5s found")
            print("\n".join(md5_matches))
            return None

        md5 = md5_matches[0]

        if set_head:
            return replace(stash_index, head_version=md5)  # type: ignore
        else:
            return replace(stash_index, base_version=md5)  # type: ignore

    def set_base_version(self, md5: t.Optional[str]):
        """Set the base (older) file version (with MD5 prefix).

        If no ID is specified, default to second most recent release
        """
        stash_index = self.read_index()
        if not stash_index:
            self.log.error("Could not set base version; no stash index found")
            return

        updated = self.set_active_base_or_head_version(stash_index, md5=md5, set_base=True)
        if updated:
            self.write_index(updated)

    def set_head_version(self, md5: t.Optional[str]):
        """Set the head (newer) or base (older) file version (with MD5 prefix).

        If no ID is specified,
            If set_head is True, default to latest export
            If set_base is True, default to second most recent export
        """

        stash_index = self.read_index()
        if not stash_index:
            self.log.error("Could not set head version; no stash index found")
            return

        updated = self.set_active_base_or_head_version(stash_index, md5, set_head=True)
        if updated:
            self.write_index(updated)

    def fetch_catalog(self) -> DblpRdfCatalog:
        return self.dblp_file_fetcher.fetch_catalog()

    def create_or_update(self):
        self.ensure_dirs()

        catalog = self.fetch_catalog()
        stash_index = StashIndex.from_catalog(catalog)

        if (existing_index := self.read_index()):
            self.log.info("Replacing exiting stash index")
            stash_index = self.update_index(old_index=existing_index, new_index=stash_index)

        self.write_index(stash_index)

    def downloaded_indicator(self, file: DblpRdfFile) -> str:
        file_dir = file.md5
        dir_exists = path.isdir(path.join(self.downloads_dir, file_dir))
        file_exists = path.isfile(path.join(self.downloads_dir, file_dir, file.filename))

        indicator = "✓" if dir_exists and file_exists else "✗"
        return indicator

    def base_head_indicator(self, index: StashIndex, file: DblpRdfFile) -> str:
        base = "<-base " if index.base_version == file.md5 else ""
        head = "<-head" if index.head_version == file.md5 else ""

        return f"{base}{head}".strip()

    def create_report(self) -> str:
        stash_index = self.read_index()
        if not stash_index:
            self.log.warn("Stash index not found")
            return "<could not build table>"

        headers = ["RDF file", "MD5 prefix", "Downloaded?", "Base/Head"]
        latest = stash_index.catalog.latest_release
        rows = [
            [
                version.filename,
                version.md5[:6],
                self.downloaded_indicator(version),
                self.base_head_indicator(stash_index, version),
            ]
            for version in [latest, *stash_index.catalog.get_archived_releases()]
        ]

        return format_table(headers, rows)
