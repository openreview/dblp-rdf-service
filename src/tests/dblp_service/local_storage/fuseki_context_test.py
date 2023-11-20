from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
from tests.dblp_service.local_storage.fixtures import *  # noqa

# from dblp_service.local_storage.fuseki_context import FusekiServerManager

async def test_update_fetch(fuseki_manager):
    # async with FusekiServerManager():
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
    ret = sparql.queryAndConvert()
    pprint(ret)
