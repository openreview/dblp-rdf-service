from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import typing as t

from dblp_service.rdfdb.fuseki_context import FusekiServerManager

import pytest

@pytest.mark.asyncio
async def test_update_fetch():
    async with FusekiServerManager() as manager:
        sparql = SPARQLWrapper("http://localhost:3030/" "ds")
        sparql.setReturnFormat(JSON)

        sparql.setQuery(
            """
            PREFIX ex: <http://example.org/>
            INSERT DATA {
                ex:subject1 ex:predicate1 "object1" .
            }
            """
        )
        print("Updating")
        update = sparql.queryAndConvert()
        pprint(update)

        print("Querying")
        sparql.setQuery(
            """
            SELECT ?s ?r ?o
            WHERE { ?s ?r ?o }
            """
        )
        ret: t.Any = sparql.queryAndConvert()
        pprint(ret)
