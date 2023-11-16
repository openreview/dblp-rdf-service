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

from marshmallow_dataclass import dataclass
from marshmallow import Schema
import marshmallow as mm

from dblp_service.lib.predef.config import Config
from dblp_service.lib.predef.log import create_logger
from dblp_service.lib.predef.tables import format_table
from dblp_service.rdfdb.dblp_rdf_catalog import DblpOrgFileFetcher, DblpRdfCatalog, DblpRdfFile
from dblp_service.rdfdb.fetch_dblp_files import get_file_md5
from shutil import copyfile
from icecream import ic


@dataclass
class StashIndex:
    catalog: DblpRdfCatalog
    base_version: t.Optional[str]  # md5
    head_version: t.Optional[str]  # md5
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema

    @classmethod
    def from_catalog(cls, catalog: DblpRdfCatalog):
        latest_md5 = catalog.latest_release.md5
        previous_md5 = catalog.most_recent_archived_rdf().md5
        return cls(catalog, base_version=previous_md5, head_version=latest_md5)


class FileStash:
    root_dir: str
    downloads_dir: str
    imports_dir: str
    index_file: str
    dblp_file_fetcher: DblpOrgFileFetcher

    log = create_logger("FileStash")

    def __init__(self, config: Config):
        service_root = config.dblpServiceRoot
        self.root_dir = path.join(service_root, "stash")
        self.downloads_dir = path.join(self.root_dir, "downloads")
        self.imports_dir = path.join(self.root_dir, "imports")
        self.index_file = path.join(self.root_dir, "stash-index.json")
        self.dblp_file_fetcher = DblpOrgFileFetcher()

    def write_index(self, stash_index: StashIndex) -> None:
        content = StashIndex.Schema().dumps(stash_index)  # type: ignore
        with open(self.index_file, "w") as f:
            f.write(content)

    def read_index(self) -> t.Optional[StashIndex]:
        if not os.path.exists(self.index_file):
            return None

        self.log.debug(f"loading index {self.index_file}")
        with open(self.index_file, "r") as f:
            content = f.read()
            sindex: StashIndex = StashIndex.Schema().loads(content)  # type: ignore
            return sindex

    def ensure_dirs(self):
        if not os.path.exists(self.root_dir):
            os.makedirs(self.root_dir)

        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)

        if not os.path.exists(self.imports_dir):
            os.makedirs(self.imports_dir)

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

    def get_all_stashed_md5s(self) -> t.List[str]:
        md5s = [md5 for md5, _ in [path.split(f) for f in self.get_imported_files()]]
        if sindex := self.read_index():
            c = sindex.catalog
            archived_md5s = [f.md5 for f in c.get_archived_releases()]
            md5s.extend(archived_md5s)
            md5s.append(c.latest_release.md5)

        return md5s

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

        # md5_matches = [v.md5 for v in catalog.get_archived_releases() if v.md5.startswith(md5)]
        md5_matches = [stashed_md5 for stashed_md5 in self.get_all_stashed_md5s() if stashed_md5.startswith(md5)]

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

        if sindex := self.read_index():
            if updated := self.set_active_base_or_head_version(sindex, md5=md5, set_base=True):
                self.write_index(updated)
                return

        self.log.error("Base version not set")

    def set_head_version(self, md5: t.Optional[str]):
        """Set the head (newer) or base (older) file version (with MD5 prefix).

        If no ID is specified,
            If set_head is True, default to latest export
            If set_base is True, default to second most recent export
        """

        if sindex := self.read_index():
            if updated := self.set_active_base_or_head_version(sindex, md5=md5, set_head=True):
                self.write_index(updated)
                return

        self.log.error("Head version not set")

    def fetch_catalog(self) -> DblpRdfCatalog:
        return self.dblp_file_fetcher.fetch_catalog()

    def init(self):
        self.ensure_dirs()
        if not (current_index := self.read_index()):
            self.create_or_update()

    def create_or_update(self):
        self.ensure_dirs()
        catalog = self.fetch_catalog()
        updated_index = StashIndex.from_catalog(catalog)
        if current_index := self.read_index():
            self.log.debug("Updating exiting stash index")
            updated_index = self.update_index(old_index=current_index, new_index=updated_index)

        self.write_index(updated_index)

    def downloaded_indicator(self, file: DblpRdfFile) -> str:
        file_dir = file.md5
        dir_exists = path.isdir(path.join(self.downloads_dir, file_dir))
        file_exists = path.isfile(path.join(self.downloads_dir, file_dir, file.filename))

        indicator = "✓" if dir_exists and file_exists else "✗"
        return indicator

    # def base_head_indicator(self, index: StashIndex, file: DblpRdfFile) -> str:
    def base_head_indicator(self, index: StashIndex, md5: str) -> str:
        base = "<-base " if index.base_version == md5 else ""
        head = "<-head" if index.head_version == md5 else ""

        return f"{base}{head}".strip()

    def create_report(self) -> str:
        stash_index = self.read_index()
        if not stash_index:
            self.log.warn("No stash index found")
            return ""

        headers = ["RDF file", "MD5 prefix", "Downloaded?", "Base/Head"]
        latest = stash_index.catalog.latest_release
        rows = [
            [
                version.filename,
                version.md5[:6],
                self.downloaded_indicator(version),
                self.base_head_indicator(stash_index, version.md5),
            ]
            for version in [latest, *stash_index.catalog.get_archived_releases()]
        ]
        for import_file in self.get_imported_files():
            md5, name = path.split(import_file)
            bh_indicator = self.base_head_indicator(stash_index, md5)
            dl_indicator = "-"
            row = [name, md5[:6], dl_indicator, bh_indicator]
            rows.append(row)

        return format_table(headers, rows)

    def get_imported_files(self) -> t.List[str]:
        files: t.List[str] = []

        md5_dirs = os.listdir(self.imports_dir)
        md5_dirs = [path.join(self.imports_dir, dir) for dir in md5_dirs]

        for md5_dir in md5_dirs:
            imported_files = os.listdir(md5_dir)
            imported_files = [path.join(md5_dir, dir) for dir in imported_files]
            if len(imported_files) != 1:
                self.log.error(f"no file found in {md5_dir} (or more than 1 file found)")
                continue
            file = imported_files[0]
            name = path.basename(file)
            dir = path.basename(path.dirname(file))

            files.append(path.join(dir, name))

        return files

    def import_file(self, filename: str) -> None:
        file_md5 = get_file_md5(filename)
        import_dir = path.join(self.imports_dir, file_md5)
        basename = path.basename(filename)
        os.makedirs(import_dir, exist_ok=True)
        dest_file = path.join(import_dir, basename)
        if path.isfile(dest_file):
            self.log.info(f"import exists: {dest_file}")
            return

        self.log.info(f"importing {filename} to {dest_file}")
        copyfile(filename, dest_file)
