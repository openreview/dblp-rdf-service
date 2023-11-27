import click
from rich.pretty import pprint
from bigtree.tree.export import print_tree
from dblp_service.pub_formats.bibtex.bibtex_transform import dblp_reprs_to_bibtex_library, print_library
from dblp_service.pub_formats.rdf_tuples.queries import get_author_publication_tree, run_author_publication_query
from dblp_service.pub_formats.rdf_tuples.tree_traversal import all_authorship_trees_to_reprs
from dblp_service.pub_formats.rdf_tuples.trees import iter_subj_obj_relationships, simplify_urlname
from dblp_service.lib.log import create_logger

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
@click.option('--show-tuples', is_flag=True, default=False)
@click.option('--step-debug', is_flag=True, default=False)
@click.option('--pub-index', type=int, default=-1)
def show_authorship(
    author_uri: str,
    format: str,
    show_tree: bool,
    show_repr: bool,
    show_tuples: bool,
    step_debug: bool,
    pub_index: int,
):
    tree = get_author_publication_tree(author_uri)
    pub_count = len(tree.children)
    log.info(f'Publication Count: {pub_count}')
    if pub_index > -1:
        if pub_index > pub_count:
            print(f'Specify pub. number <= {pub_count-1}')
        child = tree.children[pub_index]
        print(f'Only processing publication #{pub_index}')
        tree.children = (child,)


    if show_tuples:
        print('Tuples')
        for child in tree.children:
            for tuple in iter_subj_obj_relationships(child):
                printable = [t.node_name for t in tuple if t]
                # printable = [simplify_urlname(t.node_name) for t in tuple if t]
                print(printable)
        print('\n\n')

    if show_tree:
        print('Tree')
        print_tree(tree, all_attrs=True)
        print('\n\n')

    dblp_repr = all_authorship_trees_to_reprs(tree, step_debug)

    if show_repr:
        pprint(dblp_repr)

    if format.lower() == 'bibtex':
        log.info('Output==Bibtex')
        library = dblp_reprs_to_bibtex_library(dblp_repr)
        print_library(library)
        return

    log.info('Output==XML')
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
