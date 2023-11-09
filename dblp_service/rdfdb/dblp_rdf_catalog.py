from bs4 import BeautifulSoup, Tag
import typing as t

from marshmallow_dataclass import dataclass
from marshmallow import Schema
import marshmallow as mm

from dblp_service.lib.predef.log import create_logger
from dblp_service.rdfdb.fetch_dblp_files import fetch_file_content


DBLP_RELEASE_URL = "https://dblp.org/rdf/release"


@dataclass
class DblpRdfFile:
    filename: str
    md5: str
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema  # For the type checker

    @staticmethod
    def sortkey(f: "DblpRdfFile") -> str:
        return f.filename


@dataclass
class DblpRdfCatalog:
    latest_release: DblpRdfFile
    archived_releases: t.List[DblpRdfFile]
    Schema: t.ClassVar[t.Type[mm.Schema]] = Schema

    def get_archived_releases(self) -> t.List[DblpRdfFile]:
        releases = sorted(self.archived_releases, key=DblpRdfFile.sortkey)
        return list(reversed(releases))

    def most_recent_archived_rdf(self) -> DblpRdfFile:
        return self.get_archived_releases()[0]


class DblpOrgFileFetcher:
    log = create_logger("DblpOrgFileFetcher")

    def __init__(self):
        pass

    def fetch_catalog(self) -> DblpRdfCatalog:
        latest_release = self.fetch_latest_release()
        archived_releases = self.fetch_archived_releases()
        return DblpRdfCatalog(latest_release=latest_release, archived_releases=archived_releases)

    def fetch_latest_release(self) -> DblpRdfFile:
        latest_filename = "dblp.nt.gz"
        latest_url = f"https://dblp.org/rdf/{latest_filename}"
        latest_md5_url = f"{latest_url}.md5"
        latest_hash = self.fetch_md5_hash(latest_md5_url)
        return DblpRdfFile(latest_filename, latest_hash)

    def fetch_md5_hash(self, url: str) -> str:
        content = fetch_file_content(url)
        md5_hash, _ = content.split()
        return md5_hash

    def fetch_archived_releases_html(self) -> str:
        return fetch_file_content(DBLP_RELEASE_URL)

    def fetch_archived_releases(self) -> t.List[DblpRdfFile]:
        """
        """
        self.log.info("fetching dblp.org/rdf/release catalog")
        html = self.fetch_archived_releases_html()

        # Parse the content with BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")

        def is_rdf_file(tag: Tag) -> bool:
            is_a_tag = tag.name == "a"
            text = tag.text.strip()
            return is_a_tag and text.startswith("dblp") and text.endswith(".nt.gz")

        links = soup.find_all(is_rdf_file)
        self.log.info(f"found {len(links)} <a /> tags")

        releases: t.List[DblpRdfFile] = []
        for link in links:
            link_text: str = link.get_text(strip=True)

            if "href" not in link.attrs:
                raise Exception("No href attr found in dblp file link: {link}")

            location = link["href"]
            md5_url = f"{DBLP_RELEASE_URL}/{location}.md5"
            md5_hash = self.fetch_md5_hash(md5_url)
            rec = DblpRdfFile(filename=link_text, md5=md5_hash)
            self.log.info(f"fetched {rec}")
            releases.append(rec)

        return releases
