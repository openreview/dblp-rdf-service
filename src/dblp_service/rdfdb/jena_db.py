from os import getcwd, path
from SPARQLWrapper import SPARQLWrapper, JSON

import typing as t

from dblp_service.lib.predef.config import Config
from dblp_service.lib.predef.filesys import ensure_directory
from dblp_service.lib.predef.log import AppLogger, create_logger
from dblp_service.rdfdb.file_stash_manager import FileStash
from dblp_service.rdfdb.fuseki_context import FusekiServerManager
from dblp_service.rdfdb.graph_naming import GraphName, md5_to_graph_name, uri_to_graph_name
from dblp_service.rdfdb.sparql import run_sparql_update, unwrap_query_vars


class JenaDB:
    fstash: FileStash
    log: AppLogger

    def __init__(self, fstash: FileStash):
        self.fstash = fstash
        self.log = create_logger(self.__class__.__name__)

    def load_stashed_graph(self, md5: str):
        """Load the RDF file into a named graph."""
        if stashed_file := self.fstash.get_stashed_file(md5):
            graph_name = md5_to_graph_name(md5)
            file_uri = f'<file://{stashed_file.path}>'
            results = self.run_sparql_update(f'LOAD {file_uri} INTO GRAPH {graph_name.uri()}')
            assert results['statusCode'] == 200
        else:
            self.log.warn(f'Stashed id found but no file located. md5={md5}')

    def get_named_graphs(self) -> t.List[GraphName]:
        query = """ SELECT ?g WHERE {GRAPH ?g { }} """
        graph_names = [r for [r] in self.run_sparql_query(query)]
        return [uri_to_graph_name(g) for g in graph_names]

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

    def run_sparql_query(self, query: str):
        self.log.debug(f'Running query `{query}`')
        try:
            sparql = SPARQLWrapper('http://localhost:3030/' 'ds')
            sparql.setReturnFormat(JSON)
            sparql.setQuery(query)
            sparql.setMethod('GET')
            ret: t.Any = sparql.queryAndConvert()
            return unwrap_query_vars(ret)
        except:
            raise

    def run_sparql_update(self, query: str):
        try:
            self.log.debug(f'Running update `{query}`')
            sparql = SPARQLWrapper('http://localhost:3030/' 'ds')
            sparql.setReturnFormat(JSON)
            sparql.setQuery(query)
            sparql.setMethod('POST')
            ret: t.Any = sparql.queryAndConvert()
            return ret
        except:
            raise


async def init_db(config: Config):
    """
    Ensure that db exists on filesys.
    Create if not.
    report on: location, env, existing graphs, tuple counts
    """
    dbloc = config.jena.dbLocation
    success, msg = ensure_directory(dbloc)
    print(msg)
    if not success:
        print('could not initialize db')
        return

    async with FusekiServerManager(db_location=dbloc):
        pass


# - Rename the database 'current-dblp' to 'prev-dblp'
# ADD GRAPH <current-dblp> TO GRAPH <prev-dblp>
#
# # Drop the old 'current-dblp'
# DROP GRAPH <current-dblp>
#
## Copy 'updated-dblp' to 'current-dblp'
# ADD GRAPH <updated-dblp> TO GRAPH <current-dblp>
#
# Drop the old 'updated-dblp'
# DROP GRAPH <updated-dblp>
# - Rename the database 'updated-dblp' to 'current-dblp'


async def load_named_graph(ttl_file: str, graph: str, /, db_location: t.Optional[str] = None):
    cwd = getcwd()
    rdf_file = path.join(cwd, ttl_file)
    async with FusekiServerManager(db_location=db_location):
        results = run_sparql_update(f'LOAD <file://{rdf_file}> INTO GRAPH {graph} ')
        assert results['statusCode'] == 200


async def create_named_graph(graph: str, /, db_location: t.Optional[str] = None):
    async with FusekiServerManager(db_location=db_location):
        results = run_sparql_update(f'CREATE GRAPH <{graph}>')
        assert results['statusCode'] == 200


async def delete_named_graph(graph: str, /, db_location: t.Optional[str] = None):
    async with FusekiServerManager(db_location=db_location):
        results = run_sparql_update(f'DROP GRAPH <{graph}>')
        assert results['statusCode'] == 200
