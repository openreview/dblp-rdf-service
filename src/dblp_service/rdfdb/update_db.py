#!/usr/bin/env python3

# Write a set of sparql queries for the Apache Jena RDF database.
# Assume that there is an existing named graph in the Jena database named 'current-dblp'
# The queries should do the following:
# - Load the contents of a local rdf ttl (turtle) file named 'dblp.ttl' inta a new graph named 'updated-dblp'
# LOAD <file:///path/to/dblp.ttl> INTO GRAPH <updated-dblp>
#
#
# - Rename the database 'current-dblp' to 'prev-dblp'
# ADD GRAPH <current-dblp> TO GRAPH <prev-dblp>

# # Drop the old 'current-dblp'
# DROP GRAPH <current-dblp>

## Copy 'updated-dblp' to 'current-dblp'
# ADD GRAPH <updated-dblp> TO GRAPH <current-dblp>

# Drop the old 'updated-dblp'
# DROP GRAPH <updated-dblp>
 # - Rename the database 'updated-dblp' to 'current-dblp'

from dblp_service.rdfdb.fuseki_context import FusekiServerManager
from dblp_service.rdfdb.sparql import run_sparql_update
from os import getcwd, path
import typing as t


async def load_named_graph(ttl_file: str, graph: str, /, db_location: t.Optional[str] = None):
    cwd = getcwd()
    rdf_file = path.join(cwd, ttl_file)
    async with FusekiServerManager(db_location=db_location):
        results = run_sparql_update(f"LOAD <file://{rdf_file}> INTO GRAPH {graph} ")
        assert results["statusCode"] == 200

async def create_named_graph(graph: str, /, db_location: t.Optional[str] = None):
    async with FusekiServerManager(db_location=db_location):
        results = run_sparql_update(f"CREATE GRAPH <{graph}>")
        assert results["statusCode"] == 200

async def delete_named_graph(graph: str, /, db_location: t.Optional[str] = None):
    async with FusekiServerManager(db_location=db_location):
        results = run_sparql_update(f"DROP GRAPH <{graph}>")
        assert results["statusCode"] == 200
