#!/bin/env python

import click
from rdf_service.author_tree_transforms import authorship_tree_to_xml, print_xml, rewrite_authorship_tree
from bigtree.tree.export import print_tree

from rdf_service.queries import (
    # abbreviate_author_tuples,
    get_author_publication_tree,
    run_author_publication_query,
)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("author-uri", type=str)
@click.option("--rewrite", is_flag=True)
def show_authorship_tree(author_uri: str, rewrite: bool):
    tree = get_author_publication_tree(author_uri)
    if rewrite:
        rewrite_authorship_tree(tree)

    print_tree(tree, all_attrs=True)


@cli.command()
@click.argument("author-uri", type=str)
def show_authorship_xml(author_uri: str):
    tree = get_author_publication_tree(author_uri)
    rewrite_authorship_tree(tree)
    xml = authorship_tree_to_xml(tree)
    print_xml(xml)


@cli.command()
@click.argument("author-uri", type=str)
@click.option("--abbrev", is_flag=True)
def show_authorship_tuples(author_uri: str, abbrev: bool):
    tuples = run_author_publication_query(author_uri)
    for tuple in tuples:
        print(tuple)
        pass
    # if abbrev:
    #     abbrevs = abbreviate_author_tuples(tuples)
    #     for a in abbrevs:
    #         print(a)


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print("Exception")
        print(e)
