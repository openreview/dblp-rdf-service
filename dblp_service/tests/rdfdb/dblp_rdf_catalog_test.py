import unittest
from unittest import mock
from dblp_service.lib.predef.config import setenv
from dblp_service.rdfdb.dblp_rdf_catalog import DblpOrgFileFetcher, DblpRdfCatalog, DblpRdfFile

from dblp_service.tests.helpers import callable_fqn, method_fqn


setenv("test")

most_recent_rdf_file = DblpRdfFile(filename="dblp.nt.gz", md5="0ba5a47ff1d882686b2e9553a886739c")

timestamped_rdf_files = [
    DblpRdfFile(filename="dblp-2023-11-03.nt.gz", md5="88cc90ebdd04bac3cdf72bf1ac878b58"),
    DblpRdfFile(filename="dblp-2023-10-01.nt.gz", md5="4aa22d6b038ceef3849a7423fcf15365"),
    DblpRdfFile(filename="dblp-2023-09-01.nt.gz", md5="572661d887a04191893bb29beef61768"),
    DblpRdfFile(filename="dblp-2023-08-01.nt.gz", md5="1a97d3506208d99592be9ade9012763b"),
    DblpRdfFile(filename="dblp-2023-07-03.nt.gz", md5="6bc3587d2af5c39b72e664baed29d3b5"),
]
timestamped_rdf_md5s = [f.md5 for f in timestamped_rdf_files]
html_links = [f"<a href='{f.filename}'> {f.filename} </a>" for f in timestamped_rdf_files]


class DblpRdfCatalogTest(unittest.TestCase):
    @mock.patch(method_fqn(DblpOrgFileFetcher.fetch_md5_hash))
    @mock.patch(method_fqn(DblpOrgFileFetcher.fetch_archived_releases_html))
    def test_fetch_catalog(self, mock_fetch_html: mock.Mock, mock_fetch_md5: mock.Mock):
        mock_fetch_html.return_value = f'<html><body>{" ".join(html_links)}</body></html>'
        mock_fetch_md5.side_effect = [most_recent_rdf_file.md5, *timestamped_rdf_md5s]

        dblp_fetcher = DblpOrgFileFetcher()

        catalog = dblp_fetcher.fetch_catalog()
        expected_catalog = DblpRdfCatalog(
            latest_release=most_recent_rdf_file,
            archived_releases=timestamped_rdf_files,
        )
        self.assertEqual(catalog.get_archived_releases(), expected_catalog.get_archived_releases())

    def test_catalog_accessors(self):
        catalog1 = DblpRdfCatalog(
            latest_release=most_recent_rdf_file,
            archived_releases=timestamped_rdf_files,
        )
        # verify that inital sort of archived_releases does not matter
        catalog2 = DblpRdfCatalog(
            latest_release=most_recent_rdf_file,
            archived_releases=list(reversed(timestamped_rdf_files)),
        )

        recent1 = catalog1.most_recent_archived_rdf()
        recent2 = catalog2.most_recent_archived_rdf()
        recent_expect = timestamped_rdf_files[0]

        self.assertEqual(recent1, recent_expect)
        self.assertEqual(recent2, recent_expect)
