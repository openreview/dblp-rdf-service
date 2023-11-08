"""Maintain downloaded and import files in a local cache .

Stash directory structure is
- stash-root
  - downloads/
    - 3df2c/
    - ...

"""

from dataclasses import replace
from bs4 import BeautifulSoup, Tag
import typing as t
from os import path
import os

# from dataclasses import field
from marshmallow_dataclass import dataclass
from marshmallow import Schema
import marshmallow as mm

from dblp_service.lib.predef.config import Config
from dblp_service.lib.predef.log import create_logger
from dblp_service.rdfdb.fetch_dblp_files import fetch_file_content

log = create_logger(__file__)


@dataclass
class DblpRdfFile:
    filename: str
    md5: str
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema  # For the type checker


def dblp_file_sortkey(f: DblpRdfFile) -> str:
    return f.filename


@dataclass
class DblpRdfCatalog:
    latest: DblpRdfFile
    versions: t.List[DblpRdfFile]
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema

    def get_versions(self) -> t.List[DblpRdfFile]:
        versions = sorted(self.versions, key=dblp_file_sortkey)
        return list(reversed(versions))

    def get_most_recent_version(self) -> DblpRdfFile:
        return self.get_versions()[0]

    def get_prior_version(self, f: DblpRdfFile) -> t.Optional[DblpRdfFile]:
        versions = self.get_versions()
        for i, v in enumerate(versions):
            if v.md5 == f.md5 and i + 1 < len(versions):
                return versions[i + 1]

    def get_version_date_range(self) -> t.Tuple[str, str]:
        versions = self.get_versions()
        dates = [v.filename[5:][:-6] for v in versions]
        return (dates[-1], dates[0])


@dataclass
class StashIndex:
    catalog: DblpRdfCatalog
    base_version: str  # md5
    head_version: str  # md5
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema


def get_stash_root_dir(config: Config) -> str:
    return path.join(config.dblpServiceRoot, "stash")


def get_stash_index_file(config: Config) -> str:
    return path.join(get_stash_root_dir(config), "stash-index.json")


def get_stash_downloads_root(config: Config) -> str:
    return path.join(get_stash_root_dir(config), "downloads")


def get_md5_cache_dir(config: Config) -> str:
    return path.join(get_stash_root_dir(config), "md5-cache")


def write_stash_index(config: Config, stash_index: StashIndex) -> None:
    index_file = get_stash_index_file(config)
    content = StashIndex.Schema().dumps(stash_index)  # type: ignore
    with open(index_file, "w") as f:
        f.write(content)


def read_stash_index(config: Config) -> t.Optional[StashIndex]:
    index_file = get_stash_index_file(config)
    if not os.path.exists(index_file):
        return None

    with open(index_file, "r") as f:
        content = f.read()
        sindex: StashIndex = StashIndex.Schema().loads(content)  # type: ignore
        return sindex


def create_stash_dirs(config: Config):
    root = get_stash_root_dir(config)
    dl = get_stash_downloads_root(config)
    if not os.path.exists(root):
        os.makedirs(root)

    if not os.path.exists(dl):
        os.makedirs(dl)


def fetch_dblp_file_catalog() -> DblpRdfCatalog:
    latest_filename = "dblp.nt.gz"
    latest_url = f"https://dblp.org/rdf/{latest_filename}"
    latest_md5_url = f"{latest_url}.md5"
    latest_hash = fetch_md5_hash(latest_md5_url)
    latest_file = DblpRdfFile(latest_filename, latest_hash)
    dblp_releases = fetch_dblp_releases()
    catalog = DblpRdfCatalog(latest=latest_file, versions=dblp_releases)
    return catalog


def update_stash_index(*, old_index: StashIndex, new_index: StashIndex) -> StashIndex:
    return replace(
        new_index,
        base_version=old_index.base_version,
        head_version=old_index.head_version,
    )


def set_stash_base_and_head_versions(
    stash_index: StashIndex, md5: t.Optional[str], *, set_base: bool = False, set_head: bool = False
) -> t.Optional[StashIndex]:
    """Set the head (newer) or base (older) file version (with MD5 prefix).

    If no ID is specified,
        If set_head is True, default to latest export
        If set_base is True, default to second most recent export
    """
    exactly_one_set = set_base ^ set_head

    if not exactly_one_set:
        log.warning("Could not set base/head versions; Specify exactly one of set_base or set_head")
        return

    set_which = "head" if set_head else "base"

    catalog = stash_index.catalog
    most_recent_archived_version = catalog.get_most_recent_version()

    if not md5:
        if set_head:
            md5 = catalog.latest.md5
            updated = replace(stash_index, head_version=md5)
        else:
            md5 = most_recent_archived_version.md5
            updated = replace(stash_index, base_version=md5)
        return updated

    md5_matches = [v.md5 for v in catalog.get_versions() if v.md5.startswith(md5)]
    # md5_occurrances = [v.md5.startswith(md5) for v in catalog.get_versions()]

    num_matches = len(md5_matches)

    if num_matches == 0:
        log.warning(f"Could not set {set_which} version; Specified MD5 not found")
        return None

    if num_matches > 1:
        log.warning(f"Could not set {set_which} version; Multiple matching MD5s found")
        print("\n".join(md5_matches))
        return None

    md5 = md5_matches[0]

    if set_head:
        return replace(stash_index, head_version=md5)
    else:
        return replace(stash_index, base_version=md5)


def set_base_and_head(config: Config, md5: t.Optional[str], *, set_base: bool = False, set_head: bool = False):
    """Set the head (newer) or base (older) file version (with MD5 prefix).

    If no ID is specified,
        If set_head is True, default to latest export
        If set_base is True, default to second most recent export
    """
    exactly_one_set = set_base ^ set_head
    if not exactly_one_set:
        log.warning("Could not set base/head versions; Specify exactly one of set_base or set_head")
        return

    set_which = "head" if set_head else "base"

    stash_index = read_stash_index(config)
    if not stash_index:
        log.error(f"Could not set {set_which} version; no stash index found")
        return

    updated = set_stash_base_and_head_versions(stash_index, md5=md5, set_base=set_base, set_head=set_head)
    if updated:
        write_stash_index(config, updated)


def create_or_update_stash(config: Config):
    create_stash_dirs(config)
    existing_stash_index = read_stash_index(config)
    log.info("existing stash index:")

    catalog = fetch_dblp_file_catalog()
    latest_md5 = catalog.latest.md5
    new_stash_index = StashIndex(catalog=catalog, base_version=latest_md5, head_version=latest_md5)
    if existing_stash_index:
        log.info("Replacing exiting stash index")
        new_stash_index = update_stash_index(old_index=existing_stash_index, new_index=new_stash_index)
    write_stash_index(config, new_stash_index)


def fetch_md5_hash(url: str) -> str:
    content = fetch_file_content(url)
    md5_hash, _ = content.split()
    return md5_hash


DBLP_RELEASE_URL = "https://dblp.org/rdf/release"


def fetch_dblp_org_rdf_release_html() -> str:
    return fetch_file_content(DBLP_RELEASE_URL)


def fetch_dblp_releases() -> t.List[DblpRdfFile]:
    """
    Extract all links from the specified webpage and create a JSON record for each.

    :param url: The URL of the webpage to extract links from.
    :return: A list of dictionaries with "name" and "loc" keys.

    Example usage:
      url = "https://dblp.org/rdf/release"
      json_records = extract_links_to_json(url)
      print(json.dumps(json_records, indent=2))
    """
    log.info("fetching dblp.org/rdf/release catalog")
    content = fetch_dblp_org_rdf_release_html()

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")

    def is_rdf_file(tag: Tag) -> bool:
        is_a_tag = tag.name == "a"
        text = tag.text.strip()
        return is_a_tag and text.startswith("dblp") and text.endswith(".nt.gz")

    links = soup.find_all(is_rdf_file)
    log.info(f"found {len(links)} <a /> tags")

    releases: t.List[DblpRdfFile] = []
    for link in links:
        link_text: str = link.get_text(strip=True)

        if "href" not in link.attrs:
            raise Exception("No href attr found in dblp file link: {link}")

        location = link["href"]
        md5_url = f"{DBLP_RELEASE_URL}/{location}.md5"
        md5_hash = fetch_md5_hash(md5_url)
        rec = DblpRdfFile(filename=link_text, md5=md5_hash)
        log.info(f"fetched {rec}")
        releases.append(rec)

    return releases


from datetime import datetime, timedelta


def create_table(strings: t.List[str]) -> str:
    """

    Example usage:
    strings = ["apple", "banana", "cherry", "date", "fig", "grape"]
    print(create_table(strings))

    """
    # Define the table header
    table_header = f"{'original':<20}{'downloaded':^20}{'date':>20}\n"
    # Initialize the table with the header
    table = table_header + "-" * len(table_header) + "\n"

    # Mock current date
    current_date = datetime.now()

    # Iterate over the list of strings and create table rows
    for index, string in enumerate(strings):
        # Check if the string has an even number of characters
        check_mark = "✓" if len(string) % 2 == 0 else ""
        # Mock a date for each entry
        mock_date = (current_date + timedelta(days=index)).strftime("%Y-%m-%d")
        # Add the row to the table
        table += f"{string:<20}{check_mark:^20}{mock_date:>20}\n"

    return table


def format_table(headers: t.List[str], rows: t.List[t.List[str]]) -> str:
    """ """

    def fmt_row(row: t.List[str]) -> str:
        cols: t.List[str] = []
        for i, h in enumerate(row):
            if i == 0:
                cols.append(f"{h:<30}")
            elif i == len(headers) - 1:
                cols.append(f"{h:^15}")
            else:
                cols.append(f"{h:^15}")
        return "".join(cols)

    table: t.List[str] = []

    table.append(fmt_row(headers))
    sep = "=" * len(table[0])
    table.append(sep)

    # Iterate over the list of strings and create table rows
    for row in rows:
        table.append(fmt_row(row))

    table.append(sep)

    return "\n".join(table)


def is_downloaded(config: Config, file: DblpRdfFile) -> str:
    downloads = get_stash_downloads_root(config)
    file_dir = file.md5
    dir_exists = path.isdir(path.join(downloads, file_dir))
    file_exists = path.isfile(path.join(downloads, file_dir, file.filename))

    indicator = "✓" if dir_exists and file_exists else "✗"
    return indicator


def base_head_indicator(index: StashIndex, file: DblpRdfFile) -> str:
    base = "<-base " if index.base_version == file.md5 else ""
    head = "<-head" if index.head_version == file.md5 else ""

    return f"{base}{head}".strip()


def create_stash_report(config: Config) -> str:
    stash_index = read_stash_index(config)
    if not stash_index:
        log.warn("Stash index not found")
        return "<could not build table>"

    headers = ["RDF file", "MD5 prefix", "Downloaded?", "Base/Head"]
    latest = stash_index.catalog.latest
    rows = [
        [
            version.filename,
            version.md5[:6],
            is_downloaded(config, version),
            base_head_indicator(stash_index, version),
        ]
        for version in [latest, *stash_index.catalog.get_versions()]
    ]
    table = format_table(headers, rows)
    return table
