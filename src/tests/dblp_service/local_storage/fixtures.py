import pytest
import structlog
from structlog.testing import LogCapture
from dblp_service.local_storage.file_stash_manager import FileStash
from dblp_service.local_storage.fuseki_context import FusekiServerManager
from dblp_service.local_storage.jena_db import JenaDB
from dblp_service.services.rdf_graph_diff import DiffEngine

from tests.dblp_service.local_storage.mock_data import test_file_stash

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

@pytest.fixture(name="log_output")
def fixture_log_output() -> LogCapture:
    return LogCapture()

@pytest.fixture(autouse=True)
def fixture_configure_structlog(log_output: LogCapture):
    structlog.configure(
        processors=[log_output]
    )
