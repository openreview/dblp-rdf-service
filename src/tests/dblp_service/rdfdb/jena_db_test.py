from dblp_service.rdfdb.fetch_dblp_files import get_file_md5

from dblp_service.rdfdb.fuseki_context import FusekiServerManager
from dblp_service.rdfdb.graph_naming import DblpGraphName
from dblp_service.rdfdb.jena_db import JenaDB

from tests.helpers import get_resource_path
from tests.dblp_service.rdfdb import fixtures # noqa


async def test_load_graph(
    fuseki_manager: FusekiServerManager,
    jena_db: JenaDB,
):
    l222_ttl_file = get_resource_path('dblp-l222.ttl')
    md5 = get_file_md5(l222_ttl_file)

    graph_name = DblpGraphName(md5)

    jena_db.load_graph(graph_name, l222_ttl_file)
    graphs = jena_db.get_named_graphs()
    print(graphs[0].uri())
    assert len(graphs) == 1
    assert graphs[0].uri() == '<http://rdfdb/g/ed2c3d>'
