
import unittest
from unittest import mock
from dblp_service.lib.predef.config import load_config, setenv

from dblp_service.tests.helpers import callable_fqn

setenv("test")

class FileStashManagerTest(unittest.TestCase):
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
    pass
