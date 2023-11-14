import tempfile
import unittest
from unittest import mock
from dblp_service.lib.predef.config import load_config, setenv
from dblp_service.rdfdb.file_stash_manager import FileStash, StashIndex

from dblp_service.tests.helpers import method_fqn
from dblp_service.rdfdb.dblp_rdf_catalog import DblpRdfCatalog, DblpRdfFile
from dblp_service.tests.rdfdb.mock_data import rolling_catalogs

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

from contextlib import contextmanager
import typing as t


@contextmanager
def test_file_stash(catalog: t.Optional[DblpRdfCatalog] = None) -> t.Generator[FileStash, t.Any, t.Any]:
    assert (config := load_config())
    with tempfile.TemporaryDirectory() as tmpdirname:
        config.dblpServiceRoot = tmpdirname
        file_stash = FileStash(config)
        file_stash.ensure_dirs()

        if catalog:
            stash_index = StashIndex.from_catalog(catalog)
            file_stash.write_index(stash_index)

        yield file_stash


class FileStashManagerTest(unittest.TestCase):
    def assert_base_version(self, file_stash: FileStash, md5: str):
        assert (stash_index := file_stash.read_index())
        self.assertEqual(stash_index.base_version, md5)

    def assert_head_version(self, file_stash: FileStash, md5: str):
        assert (stash_index := file_stash.read_index())
        self.assertEqual(stash_index.head_version, md5)

    def test_index_read_write(self):
        catalog = DblpRdfCatalog(latest_release=most_recent_rdf_file, archived_releases=timestamped_rdf_files)

        with test_file_stash() as file_stash:
            self.assertIsNone(file_stash.read_index())
            file_stash.write_index(StashIndex.from_catalog(catalog))
            self.assertIsNotNone(file_stash.read_index())

        with test_file_stash(catalog) as file_stash:
            self.assertIsNotNone(file_stash.read_index())

    def test_set_base_and_head(self):
        catalog = DblpRdfCatalog(latest_release=most_recent_rdf_file, archived_releases=timestamped_rdf_files)

        with test_file_stash(catalog) as file_stash:
            md5_curr_release = most_recent_rdf_file.md5
            md5_prev_release = timestamped_rdf_md5s[0]
            md5_prev2_release = timestamped_rdf_md5s[1]

            self.assert_head_version(file_stash, md5_curr_release)
            self.assert_base_version(file_stash, md5_prev_release)

            # set explicit base
            file_stash.set_base_version(md5_prev2_release)
            self.assert_base_version(file_stash, md5_prev2_release)

            # set default base
            file_stash.set_base_version(None)
            self.assert_base_version(file_stash, md5_prev_release)

            # set explicit head
            file_stash.set_head_version(md5_prev2_release)
            self.assert_head_version(file_stash, md5_prev2_release)

            # set default head
            file_stash.set_head_version(None)
            self.assert_head_version(file_stash, md5_curr_release)

    @mock.patch(method_fqn(FileStash.fetch_catalog))
    def test_catalog_updates_retain_base_and_head(self, mock_fetch_catalog: mock.Mock):
        successive_catalogs = list(rolling_catalogs())
        mock_fetch_catalog.side_effect = successive_catalogs

        catalog0 = successive_catalogs[0]
        catalog0_latest_md5 = catalog0.latest_release.md5
        catalog0_prev_md5 = catalog0.most_recent_archived_rdf().md5

        with test_file_stash() as file_stash:
            for c in successive_catalogs:
                c.latest_release
                file_stash.create_or_update()
                assert (index := file_stash.read_index())

                self.assertEqual(index.catalog, c)
                self.assert_head_version(file_stash, catalog0_latest_md5)
                self.assert_base_version(file_stash, catalog0_prev_md5)
