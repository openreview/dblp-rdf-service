#!/bin/env python

from dataclasses import asdict
import click
import typing as t
from rich.pretty import pprint
from bigtree.tree.export import print_tree

from lib.open_exchange.open_fetch import fetch_profile, fetch_profiles
from lib.predef.typedefs import Slice
from lib.predef.config import setenv

from rdf_io.xml_utils import print_xml
from rdf_io.xml_transform import authorship_tree_to_xml, rewrite_authorship_tree
from rdf_io.queries import (
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


def validate_slice(
    ctx: click.Context, param: click.Parameter, value: t.Optional[t.Tuple[int, int]]
) -> t.Optional[Slice]:
    if value is None:
        return None
    return Slice(start=value[0], length=value[1])


@cli.command()
@click.option("--slice", type=(int, int), callback=validate_slice)
def profiles(slice: Slice):
    """Fetch and display a list of user profiles from OpenReview"""

    setenv("dev")
    profiles = fetch_profiles(slice=slice)
    for p in profiles:
        names = p.content.names
        print(f"Profile: {names}")


@cli.command()
@click.argument("id", type=str)
def profile(id: str):
    """Fetch (by id) and display a user profile from OpenReview"""

    setenv("dev")
    profile = fetch_profile(id)
    if profile:
        pprint(asdict(profile))
    else:
        print("No Profile found")


if __name__ == "__main__":
    try:
        cli()
    except Exception as e:
        print("Exception")
        print(e)
