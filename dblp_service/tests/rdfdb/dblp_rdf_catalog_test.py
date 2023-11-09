import unittest
from unittest import mock

from dblp_service.tests.helpers import callable_fqn

class DblpRdfCatalogTest(unittest.TestCase):
    @mock.patch(callable_fqn(fetch_md5_hash))
    @mock.patch(callable_fqn(fetch_dblp_org_rdf_release_html))
    def test_fetch_dblp_file_catalog(self, mock_fetch_html: mock.Mock, mock_fetch_md5: mock.Mock):
        mock_fetch_html.return_value = f'<html><body>{" ".join(html_links)}</body></html>'
        mock_fetch_md5.side_effect = [most_recent_rdf_file.md5, *timestamped_rdf_md5s]

        catalog = fetch_dblp_file_catalog()
        expected_catalog = DblpRdfCatalog(
            latest=most_recent_rdf_file,
            versions=timestamped_rdf_files,
        )
        self.assertEqual(catalog.get_archived_versions(), expected_catalog.get_archived_versions())

    def test_catalog_updates_retain_base_and_head(self):
        catalog = DblpRdfCatalog(latest=most_recent_rdf_file, versions=timestamped_rdf_files)
        old_index = StashIndex(
            catalog=catalog,
            base_version="old-base-md5",
            head_version="old-head-md5",
        )
        new_index = StashIndex(
            catalog=catalog,
            base_version="new-base-md5",
            head_version="new-head-md5",
        )
        updated_index = update_stash_index(old_index=old_index, new_index=new_index)
        self.assertEqual(updated_index.base_version, old_index.base_version)
        self.assertEqual(updated_index.head_version, old_index.head_version)

    def test_dblp_rdf_catalog(self):
        catalog1 = DblpRdfCatalog(
            latest=most_recent_rdf_file,
            versions=timestamped_rdf_files,
        )
        # verify that inital sort of versions does not matter
        catalog2 = DblpRdfCatalog(
            latest=most_recent_rdf_file,
            versions=list(reversed(timestamped_rdf_files)),
        )

        recent1 = catalog1.most_recent_archived_rdf()
        recent2 = catalog2.most_recent_archived_rdf()
        recent_expect = timestamped_rdf_files[0]

        self.assertEqual(recent1, recent_expect)
        self.assertEqual(recent2, recent_expect)
