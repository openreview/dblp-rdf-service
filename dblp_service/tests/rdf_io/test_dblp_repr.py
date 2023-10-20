

from dblp_service.rdf_io.dblp_repr import ResourceIdentifier


def test_merge():
    r1 = ResourceIdentifier("", "r1-val")
    r2 = ResourceIdentifier("r2-val", "")
    rout = r1.merge(r2)
    print(f"rout = {rout}")
