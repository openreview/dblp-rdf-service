from dblp_service.rdfdb.fuseki_context import FusekiServerManager

import pytest
from os import getcwd, path
import typing as t

from dblp_service.rdfdb.sparql import (
    query_is_a_publication,
    query_publications_set_difference,
    run_sparql_update,
)


@pytest.mark.asyncio
async def test_load_named_graphs():
    cwd = getcwd()
    # File contains defs for 7 publication
    rdf_file1 = path.join(cwd, "resources", "dblp-l222.ttl")

    # File contains defs for 11 publication, 7 overlapping w/prev
    rdf_file2 = path.join(cwd, "resources", "dblp-l338.ttl")
    graph_1 = "<graph_1>"
    graph_2 = "<graph_2>"
    async with FusekiServerManager():
        results = run_sparql_update(f"LOAD <file://{rdf_file1}> INTO GRAPH {graph_1} ")
        assert results["statusCode"] == 200
        results = run_sparql_update(f"LOAD <file://{rdf_file2}> INTO GRAPH {graph_2} ")
        assert results["statusCode"] == 200

        pubs_graph_1: t.List[t.List[t.Any]] = query_is_a_publication(graph_1)
        assert len(pubs_graph_1) == 7

        pubs_graph_2 = query_is_a_publication(graph_2)
        assert len(pubs_graph_2) == 11

        missing_pubs = query_publications_set_difference(graph_2, graph_1)
        assert len(missing_pubs) == 4
