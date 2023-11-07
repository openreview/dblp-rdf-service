from unittest import mock

from pprint import pprint
import tempfile
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
    write_stash_index,
)
from dblp_service.tests.helpers import callable_fqn

setenv("test")


def test_stash_index_io():
    assert (config := load_config())
    rdf_file1 = DblpRdfFile("foo", "./foo", "foo-md5-hash")
    rdf_file2 = DblpRdfFile("bar", "./bar", "bar-md5-hash")
    catalog = DblpRdfCatalog(latest=rdf_file1, versions=[rdf_file2])
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
def test_fetch_dblp_file_catalog(
    mock_fetch_html: mock.Mock,
    mock_fetch_md5: mock.Mock,
):
    mock_fetch_html.return_value = '<html><body><a href="/my-loc">dblp-Jun-2001</a></body></html>'
    mock_fetch_md5.return_value = "some_hash_value"
    catalog = fetch_dblp_file_catalog()
    pprint(catalog)
