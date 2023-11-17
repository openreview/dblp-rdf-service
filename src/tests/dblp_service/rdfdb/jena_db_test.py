import pytest

from dblp_service.rdfdb.file_stash_manager import FileStash, StashedFile
from os import path
from dblp_service.rdfdb.fuseki_context import FusekiServerManager
from dblp_service.rdfdb.jena_db import JenaDB

from tests.dblp_service.rdfdb.mock_data import test_file_stash
import tests


@pytest.fixture
async def fuseki_manager():
    async with FusekiServerManager() as fsm:
        yield fsm


@pytest.fixture
def file_stash():
    with test_file_stash() as fstash:
        yield fstash


@pytest.fixture
def jena_db(file_stash: FileStash):
    return JenaDB(file_stash)


def get_resource_path(file: str) -> str:
    p = path.join(path.dirname(tests.__file__), 'resources', file)
    # ttl_exists = path.exists(ttl_file)
    # print(f'ttl-path = {ttl_file}')
    return path.normpath(p)


async def test_load_graph(
    monkeypatch: pytest.MonkeyPatch,
    fuseki_manager: FusekiServerManager,
    file_stash: FileStash,
    jena_db: JenaDB,
):
    l222_ttl_file = get_resource_path('dblp-l222.ttl')

    stashed_file = file_stash.import_file(l222_ttl_file)

    def get_file(md5: str) -> StashedFile:
        return stashed_file

    monkeypatch.setattr(file_stash, 'get_stashed_file', get_file)
    jena_db.load_stashed_graph(stashed_file.md5)


async def test_diff_graphs(
    monkeypatch: pytest.MonkeyPatch,
    fuseki_manager: FusekiServerManager,
    file_stash: FileStash,
    jena_db: JenaDB,
):
    l222_ttl_file = get_resource_path('dblp-l222.ttl')
    l338_ttl_file = get_resource_path('dblp-l338.ttl')

    l222_stashed_file = file_stash.import_file(l222_ttl_file)
    l338_stashed_file = file_stash.import_file(l338_ttl_file)

    def get_file(md5: str) -> StashedFile:
        if md5 == l222_stashed_file.md5:
            return l222_stashed_file
        if md5 == l338_stashed_file.md5:
            return l338_stashed_file
        raise

    monkeypatch.setattr(file_stash, 'get_stashed_file', get_file)
    jena_db.load_stashed_graph(l222_stashed_file.md5)
    jena_db.load_stashed_graph(l338_stashed_file.md5)

    graphs = jena_db.get_named_graphs()
    print(graphs)
