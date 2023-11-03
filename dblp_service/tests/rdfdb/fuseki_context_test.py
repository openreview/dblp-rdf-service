#!/usr/bin/env python3
from pprint import pprint
import unittest
from SPARQLWrapper import SPARQLWrapper, JSON
import typing as t

from dblp_service.rdfdb.fuseki_context import FusekiServerManager

import pytest

@pytest.mark.asyncio
async def test_startup_shutdown():
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

# class TestFusekiServerManager(unittest.TestCase):

        # After exiting the context manager, the server should be shut down
        # We can check this by attempting to connect to the server
        # response = requests.get("http://localhost:3030/")
        # self.assertNotEqual(response.status_code, 200)

    # async def test_operations(self):
    #     async with FusekiServerManager() as manager:
    #         # Assuming the server is running on the default port (3030)
    #         # and the default dataset path is /ds
    #         base_url = "http://localhost:3030/ds"

    #         # Load operation (using SPARQL Update)
    #         load_data = """
    #         PREFIX ex: <http://example.org/>
    #         INSERT DATA {
    #             ex:subject1 ex:predicate1 "object1" .
    #         }
    #         """
    #         response = requests.post(f"{base_url}/update", data={"update": load_data})
    #         self.assertEqual(response.status_code, 200)

    #         # Query operation (using SPARQL Query)
    #         query_data = """
    #         SELECT ?s ?p ?o WHERE {
    #             ?s ?p ?o .
    #         }
    #         """
    #         response = requests.get(f"{base_url}/query", params={"query": query_data})
    #         self.assertEqual(response.status_code, 200)
    #         results = response.json()
    #         self.assertIn("results", results)
    #         self.assertIn("bindings", results["results"])

    #         # Update operation (using SPARQL Update)
    #         update_data = """
    #         PREFIX ex: <http://example.org/>
    #         DELETE {
    #             ex:subject1 ex:predicate1 "object1" .
    #         } INSERT {
    #             ex:subject1 ex:predicate1 "object2" .
    #         } WHERE {
    #             ex:subject1 ex:predicate1 "object1" .
    #         }
    #         """
    #         response = requests.post(f"{base_url}/update", data={"update": update_data})
    #         self.assertEqual(response.status_code, 200)


# if __name__ == '__main__':
#     unittest.main()
