"""Maintain downloaded and import files in a local cache .

Stash directory structure is
- stash-root
  - md5-cache/
  - downloads/
    - 3df2c/
    - ...


"""

from dataclasses import replace
from pprint import pprint
from bs4 import BeautifulSoup
from typing import List
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
    location: str
    md5: str
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema  # For the type checker


@dataclass
class DblpRdfCatalog:
    latest: DblpRdfFile
    versions: t.List[DblpRdfFile]
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema  # For the type checker


@dataclass
class StashIndex:
    catalog: DblpRdfCatalog
    base_version: str  # md5
    head_version: str  # md5
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema  # For the type checker


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
    dblp_releases = fetch_dblp_releases()
    latest_filename = "dblp.nt.gz"
    latest_url = f"https://dblp.org/rdf/{latest_filename}"
    latest_md5_url = f"{latest_url}.md5"
    latest_hash = fetch_md5_hash(latest_md5_url)
    latest_file = DblpRdfFile(latest_filename, latest_url, latest_hash)
    catalog = DblpRdfCatalog(latest=latest_file, versions=dblp_releases)
    return catalog


def create_or_update_stash(config: Config):
    create_stash_dirs(config)
    existing_stash_index = read_stash_index(config)
    log.info("existing stash index:")
    pprint(existing_stash_index)

    catalog = fetch_dblp_file_catalog()
    latest_md5 = catalog.latest.md5
    new_stash_index = StashIndex(catalog=catalog, base_version=latest_md5, head_version=latest_md5)
    log.info("new stash index:")
    pprint(new_stash_index)
    if existing_stash_index:
        new_stash_index = replace(
            new_stash_index,
            base_version=existing_stash_index.base_version,
            head_version=existing_stash_index.head_version,
        )
    pprint(new_stash_index)


def fetch_md5_hash(url: str) -> str:
    content = fetch_file_content(url)
    md5_hash, _ = content.split()
    return md5_hash


def import_file(filepath: str):
    """Store file in a hash-encoded dir w/metadata."""


def fetch_dblp_org_rdf_release_html() -> str:
    url = "https://dblp.org/rdf/release"
    return fetch_file_content(url)


def fetch_dblp_releases() -> List[DblpRdfFile]:
    """
    Extract all links from the specified webpage and create a JSON record for each.

    :param url: The URL of the webpage to extract links from.
    :return: A list of dictionaries with "name" and "loc" keys.

    Example usage:
      url = "https://dblp.org/rdf/release"
      json_records = extract_links_to_json(url)
      print(json.dumps(json_records, indent=2))
    """
    content = fetch_dblp_org_rdf_release_html()

    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(content, "html.parser")
    links = soup.find_all("a")  # Find all <a> tags

    releases: List[DblpRdfFile] = []
    for link in links:
        link_text: str = link.get_text(strip=True)
        if not link_text.startswith('dblp'):
            continue

        if "href" in link.attrs:
            location = link["href"]
            md5_url = f"{location}.md5"
            md5_hash = fetch_md5_hash(md5_url)
            rec = DblpRdfFile(filename=link.get_text(strip=True), location=link["href"], md5=md5_hash)
            releases.append(rec)

    return releases
