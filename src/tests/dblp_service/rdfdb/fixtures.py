import pytest
from dblp_service.rdfdb.diff_engine import DiffEngine
from dblp_service.rdfdb.file_stash_manager import FileStash
from dblp_service.rdfdb.fuseki_context import FusekiServerManager
from dblp_service.rdfdb.jena_db import JenaDB

from tests.dblp_service.rdfdb.mock_data import test_file_stash

@pytest.fixture
async def fuseki_manager():
    async with FusekiServerManager() as fsm:
        yield fsm


@pytest.fixture
def file_stash():
    with test_file_stash() as fstash:
        yield fstash


@pytest.fixture
def jena_db():
    return JenaDB()

@pytest.fixture
def diff_engine(file_stash: FileStash, jena_db: JenaDB):
    return DiffEngine(file_stash, jena_db)
