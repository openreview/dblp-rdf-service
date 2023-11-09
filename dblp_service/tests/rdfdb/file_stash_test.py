from unittest import mock

import tempfile
import unittest
from dblp_service.lib.predef.config import load_config, setenv

from dblp_service.rdfdb.file_stash import (
    DblpRdfCatalog,
    DblpRdfFile,
    StashIndex,
    create_stash_dirs,
    fetch_dblp_org_rdf_release_html,
    fetch_dblp_file_catalog,
    fetch_md5_hash,
    read_stash_index,
    set_stash_base_and_head_versions,
    update_stash_index,
    write_stash_index,
)
from dblp_service.tests.helpers import callable_fqn

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


class FileStashTests(unittest.TestCase):
    def test_stash_index_io(self):
        assert (config := load_config())

        catalog = DblpRdfCatalog(latest=most_recent_rdf_file, versions=timestamped_rdf_files)
        dummy_stash_index = StashIndex(catalog=catalog, base_version="base-md5", head_version="head-md5")

        with tempfile.TemporaryDirectory() as tmpdirname:
            print("created temporary directory", tmpdirname)
            config.dblpServiceRoot = tmpdirname
            create_stash_dirs(config)
            nonexistant_index = read_stash_index(config)
            assert nonexistant_index is None
            write_stash_index(config, dummy_stash_index)
            existing_index = read_stash_index(config)
            assert existing_index is not None

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

    def test_set_base_and_head(self):
        catalog = DblpRdfCatalog(latest=most_recent_rdf_file, versions=timestamped_rdf_files)
        stash_index = StashIndex(
            catalog=catalog,
            base_version=most_recent_rdf_file.md5,
            head_version=most_recent_rdf_file.md5,
        )
        updated = set_stash_base_and_head_versions(stash_index, None)
        self.assertIsNone(updated)

        updated = set_stash_base_and_head_versions(stash_index, md5=None, set_base=True)
        self.assertIsNotNone(updated)
        assert updated
        self.assertEqual(updated.base_version, timestamped_rdf_md5s[0])

        updated = set_stash_base_and_head_versions(stash_index, md5=None, set_head=True)
        self.assertIsNotNone(updated)
        assert updated
        self.assertEqual(updated.base_version, most_recent_rdf_file.md5)
