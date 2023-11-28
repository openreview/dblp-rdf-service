#!/bin/env python

from dblp_service.app.cli import cli
from dblp_service.app import graph_query, stash, jena, openreview
from rich.console import Console
from rich.traceback import install

if __name__ == '__main__':
    install(show_locals=True)
    console = Console()
    clis = stash, jena, graph_query, openreview
    try:
        cli(obj={})
    except Exception as e:
        console.print_exception(show_locals=True)
