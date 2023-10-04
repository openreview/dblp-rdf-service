from collections import namedtuple
from SPARQLWrapper import SPARQLWrapper, JSON
import typing as t

AuthorTuple = namedtuple("AuthorTuple", ["sub", "pred", "obj", "bpred", "bobj"])


def run_query(authorURI: str) -> t.List[AuthorTuple]:
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
        print('error')
        print(e)

    return tuples


def get_type_val(rec, key: str) -> str:
    if key not in rec:
        raise Exception("key must be in rec")

    subrec = rec[key]
    v = subrec["value"]
    return v


def opt_type_val(rec, key: str) -> t.Optional[str]:
    if key not in rec:
        return None

    subrec = rec[key]
    t = subrec["type"]
    v = subrec["value"]
    return v
