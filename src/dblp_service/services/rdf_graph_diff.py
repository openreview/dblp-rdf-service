import typing as t

from dblp_service.lib.log import AppLogger, create_logger
from dblp_service.local_storage.file_stash_manager import FileStash
from dblp_service.local_storage.jena_db import JenaDB
from textwrap import dedent

from dblp_service.local_storage.graph_naming import DblpGraphName, DiffGraphName, GraphName, md5_to_graph_name

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

    def create_diff_graph(self, graph1: DblpGraphName, graph2: DblpGraphName) -> DiffGraphName:
        """Create a new graph containing all publications in graph1 but not graph2

        Query for difference (graph1 - graph2) for all tuples matching
        `?x a dblp:Publication`, then insert those tuples into a new graph
        """

        diff_graph = DiffGraphName(graph2, graph1)
        query_pubs = dedent(
            f"""
            PREFIX dblp: <https://dblp.org/rdf/schema#>

            INSERT {{
              GRAPH {diff_graph.uri()} {{
                ?pub a dblp:Publication
              }}
            }}
            WHERE {{
                GRAPH {graph1.uri()} {{ ?pub a dblp:Publication }}
                FILTER NOT EXISTS {{
                    GRAPH {graph2.uri()} {{ ?pub a dblp:Publication }}
                }}
            }}
            """
        )
        self.jenadb.run_sparql_update(query_pubs)
        return diff_graph

    def load_active_graphs(self):
        """"""
        head_id, base_id = self.fstash.get_base_and_head_id()
        if head_id:
            self.load_stashed_graph(head_id)
        else:
            self.log.warn(f'No file source found for head={head_id}')

        if base_id:
            self.load_stashed_graph(base_id)
        else:
            self.log.warn(f'No file source found for base={base_id}')
