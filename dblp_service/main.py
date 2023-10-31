#!/bin/env python

from dataclasses import asdict
import click
import typing as t
from rich.pretty import pprint
from bigtree.tree.export import print_tree
from dblp_service.dblp_io.bibtex_output.bibtex_transform import dblp_reprs_to_bibtex_library, print_library
from dblp_service.dblp_io.rdf_io.queries import get_author_publication_tree, run_author_publication_query
from dblp_service.dblp_io.rdf_io.tree_traversal import all_authorship_trees_to_reprs
from dblp_service.dblp_io.rdf_io.trees import simplify_urlname
from dblp_service.lib.predef.log import create_logger

from dblp_service.lib.open_exchange.open_fetch import fetch_profile, fetch_profiles
from dblp_service.lib.predef.typedefs import Slice
from dblp_service.lib.predef.config import setenv

log = create_logger(__file__)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("author-uri", type=str)
@click.option("--format", type=click.Choice(["xml", "bibtex"], case_sensitive=True), default="bibtex")
@click.option("--show-tree", is_flag=True, default=False)
@click.option("--show-repr", is_flag=True, default=False)
@click.option("--choose-pub", type=int, default=0)
def show_authorship(author_uri: str, format: str, show_tree: bool, show_repr: bool, choose_pub: int):
    tree = get_author_publication_tree(author_uri)
    pub_count = len(tree.children)
    log.info(f"Publication Count: {pub_count}")
    if choose_pub > 0:
        if choose_pub > pub_count:
            print(f"Specify pub. number <= {pub_count-1}")
        child = tree.children[choose_pub]
        print(f"Only processing publication #{choose_pub}")
        tree.children = (child,)

    if show_tree:
        print_tree(tree, all_attrs=True)

    dblp_repr = all_authorship_trees_to_reprs(tree)

    if show_repr:
        pprint(dblp_repr)

    if format.lower() == "bibtex":
        library = dblp_reprs_to_bibtex_library(dblp_repr)
        print_library(library)
        return

    # else format == 'xml'
    print("TODO")


@cli.command()
@click.argument("author-uri", type=str)
@click.option("--pub-num", type=int, default=0)
def show_authorship_tree(author_uri: str, pub_num: int):
    tree = get_author_publication_tree(author_uri)
    if pub_num > 0:
        pub = tree.children[pub_num]
        print_tree(pub, all_attrs=True)
        return

    print_tree(tree, all_attrs=True)


@cli.command()
@click.argument("author-uri", type=str)
@click.option("--abbrev", is_flag=True)
def show_authorship_tuples(author_uri: str, abbrev: bool):
    tuples = run_author_publication_query(author_uri)
    for tuple in tuples:
        printable = [(simplify_urlname(t) if abbrev else t) for t in tuple if t]
        print(printable)


def validate_slice(
    ctx: click.Context, _parm: click.Parameter, value: t.Optional[t.Tuple[int, int]]
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
