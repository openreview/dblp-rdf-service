#!/bin/env python

from dblp_service.app.cli import cli
from dblp_service.app import stash, jena, rdf_query, openreview


if __name__ == "__main__":
    clis = stash, jena, rdf_query, openreview
    try:
        cli(obj={})
    except Exception as e:
        print("Exception")
        print(e)
