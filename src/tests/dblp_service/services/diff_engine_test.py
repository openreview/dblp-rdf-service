import pytest
from dblp_service.services.diff_engine import DiffEngine

from dblp_service.local_storage.fuseki_context import FusekiServerManager
from dblp_service.local_storage.graph_naming import file_to_graph_name
from tests.dblp_service.local_storage.fixtures import *  # noqa
from tests.helpers import get_resource_path


async def test_diff_graphs(
    monkeypatch: pytest.MonkeyPatch,
    diff_engine: DiffEngine,
    fuseki_manager: FusekiServerManager
):
    l222_ttl_file = get_resource_path('dblp-l222.ttl')
    l338_ttl_file = get_resource_path('dblp-l338.ttl')
    l222_graph_name = file_to_graph_name(l222_ttl_file)
    l338_graph_name = file_to_graph_name(l338_ttl_file)

    jena_db = diff_engine.jenadb
    jena_db.load_graph(l222_graph_name, l222_ttl_file)
    jena_db.load_graph(l338_graph_name, l338_ttl_file)
    l222_pubs = diff_engine.query_is_a_publication(l222_graph_name)
    l338_pubs = diff_engine.query_is_a_publication(l338_graph_name)
    assert len(l222_pubs) == 7
    assert len(l338_pubs) == 11

    diff = diff_engine.diff_publications_graphs(l338_graph_name, l222_graph_name)
    assert len(diff) == 4

    diff_graph = diff_engine.create_diff_graph(l338_graph_name, l222_graph_name)

    diff_pubs = diff_engine.query_is_a_publication(diff_graph)
    assert len(diff_pubs) == 4
