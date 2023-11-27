"""Functions to create and manipulate graph names for JenaDB.

Two types of graphs are used in  this system: the imported RDFs for a particular
export of dblp.org, and  a graph which is a generated  diff between two dblp.org
imports. Naming conventions are adopted to distinguish between the two and help
manage updating the database.

Imported dblp.org graphs are named for the  MD5 hash (or rather, a prefix of the
MD5) of  the RDF  file that  was imported to  create the  graph, with  a leading
'/g/', e.g., '/g/3adfe8'

The full URI required by SPARQL looks like <https://server/g/23a3e>.

The naming convention is:
        qname (qualified name) = '/g/md5-prefix'
        uri = '<https://some-server/g/md5-prefix>'


Diff graphs are  named for the 2  dblp.org import graphs that  are being diffed,
e.g., '/diff/g/ea3f5g/g/3adfe8'.

This  would correspond  to the  computed set  difference /g/ea3f5g  - /g/3adfe8,
meaning all of the publications in the first graph that are not in the second.

"""
from abc import abstractmethod
import dataclasses as dc
import typing as t
import re

from dblp_service.dblp_org.fetch_dblp_files import get_file_md5


@dc.dataclass
class GraphName:
    @abstractmethod
    def qname(self) -> str:
        """return qualifed name for graph.
        e.g., /g/3sdfe
        """

    def uri(self) -> str:
        """return fully qualifed uri for graph.
        Output is form required by JenaDB
        e.g., <http://rdfdb/g/3sdfe>
        """
        return f'<http://rdfdb/{self.qname()}>'


@dc.dataclass
class DblpGraphName(GraphName):
    md5: str

    def qname(self) -> str:
        return f'g/{self.md5[:6]}'


@dc.dataclass
class DiffGraphName(GraphName):
    graph1: DblpGraphName
    graph2: DblpGraphName

    def qname(self) -> str:
        return f'diff/{self.graph1.qname()}/{self.graph2.qname()}'


def qname_path_to_graph_name(uri_path: t.List[str]) -> GraphName:
    """Convert a qname str into name repr.
    qname = 'g/**' or '/diff/g/**/g**'

    """
    assert len(uri_path) > 0
    assert all([len(s) > 0 for s in uri_path])

    match uri_path[0]:
        case 'diff':
            assert len(uri_path) == 5
            g1 = qname_path_to_graph_name(uri_path[1:3])
            g2 = qname_path_to_graph_name(uri_path[3:5])
            match (g1, g2):
                case (DblpGraphName() as g1, DblpGraphName() as g2):
                    return DiffGraphName(g1, g2)

                case _:
                    raise Exception(f'error making /diff graph name from {uri_path}')

        case 'g':
            md5 = uri_path[1]
            return DblpGraphName(md5)

        case _:
            pass

    raise Exception(f'could not construct graph name from {uri_path}')


def uri_to_graph_name(uri: str) -> GraphName:
    """Convert a URI str into name repr.

    """
    http_start = re.compile('^http://[^/]+/')
    if http_start.match(uri):
        [_, uri_tail] = http_start.split(uri)
        print(f'uri= {uri}, uri_tail = {uri_tail}')
        return qname_path_to_graph_name(uri_tail.split('/'))

    path = [p for p in uri.split('/') if len(p) > 0]
    return qname_path_to_graph_name(path)


def md5_to_graph_name(md5: str) -> DblpGraphName:
    return DblpGraphName(md5)

def file_to_graph_name(file_path: str) -> DblpGraphName:
    md5 = get_file_md5(file_path)
    return DblpGraphName(md5)
