import typing as t

from dblp_service.lib.predef.log import AppLogger, create_logger
from dblp_service.rdfdb.file_stash_manager import FileStash
from dblp_service.rdfdb.jena_db import JenaDB
from textwrap import dedent

from dblp_service.rdfdb.graph_naming import GraphName, md5_to_graph_name


class DiffEngine:
    """Compute and manage the changes between dblp.org data exports."""

    fstash: FileStash
    jenadb: JenaDB
    log: AppLogger

    def __init__(self, fstash: FileStash, jenadb: JenaDB):
        self.fstash = fstash
        self.jenadb = jenadb
        self.log = create_logger(self.__class__.__name__)

    def load_stashed_graph(self, md5: str):
        """Load the RDF file into a named graph."""
        if (stashed_file := self.fstash.get_stashed_file(md5)) is not None:
            graph_name = md5_to_graph_name(md5)
            assert (file_path := stashed_file.path) is not None
            self.jenadb.load_graph(graph_name, file_path)
        else:
            self.log.warn(f'Stashed id found but no file located. md5={md5}')

    def query_is_a_publication(self, graph: GraphName):
        query_pubs = dedent(
            f"""
            PREFIX dblp: <https://dblp.org/rdf/schema#>

            SELECT ?s WHERE {{
                GRAPH {graph.uri()} {{ ?s a dblp:Publication }}
            }}
        """
        )
        return self.jenadb.run_sparql_query(query_pubs)

    def diff_publications_graphs(self, graph1: GraphName, graph2: GraphName) -> t.List[str]:
        """Return all publications in graph1 but not graph2

        Query for difference (graph1 - graph2) for all tuples matching
        `?x a dblp:Publication`
        """
        query_pubs = dedent(
            f"""
            PREFIX dblp: <https://dblp.org/rdf/schema#>

            SELECT ?s WHERE {{
                GRAPH {graph1.uri()} {{ ?s a dblp:Publication }}
                FILTER NOT EXISTS {{
                    GRAPH {graph2.uri()} {{ ?s a dblp:Publication }}
                }}
            }}
            """
        )
        entries = self.jenadb.run_sparql_query(query_pubs)
        return [entry[0] for entry in entries]
