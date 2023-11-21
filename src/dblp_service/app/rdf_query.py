import click
from rich.pretty import pprint
from bigtree.tree.export import print_tree
from dblp_service.pub_formats.bibtex.bibtex_transform import dblp_reprs_to_bibtex_library, print_library
from dblp_service.pub_formats.rdf_tuples.queries import get_author_publication_tree, run_author_publication_query
from dblp_service.pub_formats.rdf_tuples.tree_traversal import all_authorship_trees_to_reprs
from dblp_service.pub_formats.rdf_tuples.trees import simplify_urlname
from dblp_service.lib.log import create_logger

from dblp_service.open_exchange.open_fetch import fetch_notes_for_author, fetch_profile
from dblp_service.lib.config import setenv
from .cli import cli

log = create_logger(__file__)


@cli.group()
def query():
    """Query Jena (RDF DB)"""


@query.command()
@click.argument('author-uri', type=str)
@click.option('--format', type=click.Choice(['xml', 'bibtex'], case_sensitive=True), default='bibtex')
@click.option('--show-tree', is_flag=True, default=False)
@click.option('--show-repr', is_flag=True, default=False)
@click.option('--pub-index', type=int, default=0)
def show_authorship(author_uri: str, format: str, show_tree: bool, show_repr: bool, pub_index: int):
    tree = get_author_publication_tree(author_uri)
    pub_count = len(tree.children)
    log.info(f'Publication Count: {pub_count}')
    if pub_index > 0:
        if pub_index > pub_count:
            print(f'Specify pub. number <= {pub_count-1}')
        child = tree.children[pub_index]
        print(f'Only processing publication #{pub_index}')
        tree.children = (child,)

    if show_tree:
        print_tree(tree, all_attrs=True)

    dblp_repr = all_authorship_trees_to_reprs(tree)

    if show_repr:
        pprint(dblp_repr)

    if format.lower() == 'bibtex':
        library = dblp_reprs_to_bibtex_library(dblp_repr)
        print_library(library)
        return

    # else format == 'xml'
    print('TODO')


@query.command()
@click.argument('author-uri', type=str)
@click.option('--pub-num', type=int, default=0)
def show_authorship_tree(author_uri: str, pub_num: int):
    tree = get_author_publication_tree(author_uri)
    if pub_num > 0:
        pub = tree.children[pub_num]
        print_tree(pub, all_attrs=True)
        return

    print_tree(tree, all_attrs=True)


@query.command()
@click.argument('author-uri', type=str)
@click.option('--abbrev', is_flag=True)
def show_authorship_tuples(author_uri: str, abbrev: bool):
    tuples = run_author_publication_query(author_uri)
    for tuple in tuples:
        printable = [(simplify_urlname(t) if abbrev else t) for t in tuple if t]
        print(printable)


