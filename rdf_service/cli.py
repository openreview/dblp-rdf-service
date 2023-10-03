# pyright: reportUnusedImport=false
# pyright: reportUnusedExpression=false

import click

from pprint import pprint

from rdf_service.author_query import query_author

@click.command()
@click.option("--author-id", type=str, required=True, help="find papers for the given author")
def get_authorship(authorId: str):
    query_author(authorId)


def go():
    query_author("https://dblp.org/pid/m/AndrewMcCallum")


if __name__ == "__main__":
    go()
