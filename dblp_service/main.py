#!/bin/env python

from app.cli import cli
from app import rdf_query, rdf_db

if __name__ == "__main__":
    try:
        cli(obj={})
    except Exception as e:
        print("Exception")
        print(e)
