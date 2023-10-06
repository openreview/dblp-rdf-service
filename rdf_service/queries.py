from SPARQLWrapper import SPARQLWrapper, JSON
import typing as t

from bigtree import Node, add_path_to_tree  # type: ignore


class AuthorTuple(t.NamedTuple):
    sub: str
    pred: str
    obj: str
    bpred: t.Optional[str] = None
    bobj: t.Optional[str] = None


def run_author_publication_query(authorURI: str) -> t.List[AuthorTuple]:
    sparql = SPARQLWrapper("http://localhost:3030/" "ds")
    sparql.setReturnFormat(JSON)

    sparql.setQuery(
        """
        prefix dblp: <https://dblp.org/rdf/schema#>

        SELECT ?sub ?pred ?obj ?bpred ?bobj
        WHERE {
          ?sub dblp:authoredBy """
        f"<{authorURI}> . "
        """
          {
            ?sub ?pred ?obj
            FILTER (! isBlank(?obj) )
          } UNION {
            ?sub ?pred ?obj
            FILTER (isBlank(?obj) ) .
            ?obj ?bpred ?bobj .
          }
        }
        """
    )

    tuples: t.List[AuthorTuple] = []
    try:
        ret: t.Any = sparql.queryAndConvert()

        for r in ret["results"]["bindings"]:
            sub = get_type_val(r, "sub")
            pred = get_type_val(r, "pred")
            obj = get_type_val(r, "obj")
            bpred = opt_type_val(r, "bpred")
            bobj = opt_type_val(r, "bobj")
            tuples.append(AuthorTuple(sub, pred, obj, bpred, bobj))

    except Exception as e:
        print("error")
        print(e)

    return tuples


def get_author_publication_tree(authorURI: str) -> Node:
    tuples = run_author_publication_query(authorURI)
    return create_tree_from_tuples(tuples)


def create_tree_from_tuples(tuples: t.List[AuthorTuple]) -> Node:
    sep = "|"
    root: Node = Node("root")
    for tuple in tuples:
        path = sep.join(["root"] + [p for p in tuple if p])
        add_path_to_tree(root, path=path, sep=sep)

    return root


def abbreviate_author_tuples(tuples: t.List[AuthorTuple]) -> t.List[str]:
    abbrevs: t.List[str] = []

    def trim(s: t.Optional[str]) -> str:
        if not s:
            return ""
        if s.startswith("http"):
            sp = s.split("/")
            return sp[-1]

        return s

    for tuple in tuples:
        trimmed = [trim(t) for t in tuple if t]
        x = ", ".join(trimmed)
        abbrevs.append(x)

    return abbrevs


def get_type_val(rec: t.Dict[str, t.Any], key: str) -> str:
    if key not in rec:
        raise Exception("key must be in rec")

    subrec = rec[key]
    v = subrec["value"]
    return v


def opt_type_val(rec: t.Dict[str, t.Any], key: str) -> t.Optional[str]:
    if key not in rec:
        return None

    subrec = rec[key]
    v = subrec["value"]
    return v
