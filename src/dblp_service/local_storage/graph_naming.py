"""Functions to create and manipulate graph names for JenaDB.
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
        e.g., g/3sdfe
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


def uri_path_to_graph_name(uri_path: t.List[str]) -> GraphName:
    """Convert a URI str into name repr."""
    assert len(uri_path) > 0
    assert all([len(s) > 0 for s in uri_path])

    match uri_path[0]:
        case 'diff':
            assert len(uri_path) == 5
            g1 = uri_path_to_graph_name(uri_path[1:3])
            g2 = uri_path_to_graph_name(uri_path[3:5])
            match (g1, g2):
                case (DblpGraphName() as g1, DblpGraphName() as g2):
                    return DiffGraphName(g1, g2)

                case _:
                    raise Exception(f'error making /diff graph name from {uri_path}')

        case 'g':
            return DblpGraphName(uri_path[1])

        case _:
            pass

    raise Exception(f'could not construct graph name from {uri_path}')


def uri_to_graph_name(uri: str) -> GraphName:
    """Convert a URI str into name repr."""
    uri_start = re.compile('^http://[^/]+/')
    assert uri_start.match(uri)
    [_, uri_tail] = uri_start.split(uri)
    print(f'uri= {uri}, uri_tail = {uri_tail}')
    return uri_path_to_graph_name(uri_tail.split('/'))


def md5_to_graph_name(md5: str) -> DblpGraphName:
    return DblpGraphName(md5)

def file_to_graph_name(file_path: str) -> DblpGraphName:
    md5 = get_file_md5(file_path)
    return DblpGraphName(md5)
