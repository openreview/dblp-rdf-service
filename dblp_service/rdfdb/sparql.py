from textwrap import dedent
from SPARQLWrapper import SPARQLWrapper, JSON
import typing as t
from pprint import pprint


def unwrap_query_vars(queryReturn: t.Any) -> t.List[t.List[t.Any]]:
    output: t.List[t.List[t.Any]] = []
    match queryReturn:
        case {"head": {"vars": [*varnames]}, "results": {"bindings": [*bindings]}}:
            output = [[b[var]["value"] for var in varnames] for b in bindings]

        case _:
            pprint(queryReturn)

    return output


def run_sparql_query(query: str):
    sparql = SPARQLWrapper("http://localhost:3030/" "ds")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    sparql.setMethod("GET")
    ret: t.Any = sparql.queryAndConvert()
    return unwrap_query_vars(ret)


def run_sparql_update(query: str):
    sparql = SPARQLWrapper("http://localhost:3030/" "ds")
    sparql.setReturnFormat(JSON)
    sparql.setQuery(query)
    sparql.setMethod("POST")
    ret: t.Any = sparql.queryAndConvert()
    return ret


def query_graph_names() -> t.List[str]:
    query = """ SELECT ?g WHERE {GRAPH ?g { }} """
    return [r for [r] in run_sparql_query(query)]


def query_is_a_publication(graph_name: str):
    query_pubs = dedent(
        f"""
        PREFIX dblp: <https://dblp.org/rdf/schema#>

        SELECT ?s WHERE {{
            GRAPH {graph_name} {{ ?s a dblp:Publication }}
        }}
    """
    )
    return run_sparql_query(query_pubs)


def query_publications_set_difference(graph1: str, graph2: str) -> t.List[str]:
    """Return all publications in graph1 but not graph2

    Query for difference (graph1 - graph2) for all tuples matching
    `?x a dblp:Publication`
    """
    query_pubs = dedent(
        f"""
            PREFIX dblp: <https://dblp.org/rdf/schema#>

            SELECT ?s WHERE {{
              GRAPH {graph1} {{ ?s a dblp:Publication }}
              FILTER NOT EXISTS {{
                  GRAPH {graph2} {{ ?s a dblp:Publication }}
              }}
            }}
    """
    )
    entries = run_sparql_query(query_pubs)
    return [entry[0] for entry in entries]


# Query everything in graph g1 = run_sparql_query(f"""SELECT ?s ?r ?o WHERE {{ graph {graph_1} {{  ?s ?r ?o }} }} """)
