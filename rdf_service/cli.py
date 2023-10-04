#!/bin/env python

import typing as t
import click
from rdf_service.author_query import query_author, tree_to_xml
from rdf_service.queries import run_query


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--author-id",
    type=str,
    required=True,
    help="find papers for the given author",
)
def show_authorship_tree(author_id: str):
    print("querying author...")
    tree = query_author(author_id)
    tree.show()

@cli.command()
@click.option(
    "--author-id",
    type=str,
    required=True,
    help="find papers for the given author",
)
def show_authorship_xml(author_id: str):
    tree = query_author(author_id)
    tree_to_xml(tree)



@cli.command()
@click.option(
    "--author-id",
    type=str,
    required=True,
    help="find papers for the given author",
)
def show_authorship_tuples(author_id: str):
    print(f"here: {author_id}")
    tuples = run_query(author_id)
    for tuple in tuples:
        trimmed = [trim(t) for t in tuple if t]
        x = ', '.join(trimmed)
        print(x)



def trim(s: t.Optional[str]) -> str:
    if not s: return ''
    if s.startswith('http'):
        sp = s.split('/')
        return sp[-1]

    return s



if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print('Exception')
        print(e)
