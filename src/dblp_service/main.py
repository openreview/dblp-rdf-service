#!/bin/env python

from dblp_service.app.cli import cli
from dblp_service.app import stash, rdf_db, rdf_query


if __name__ == "__main__":
    clis = stash, rdf_db, rdf_query
    try:
        cli(obj={})
    except Exception as e:
        print("Exception")
        print(e)
