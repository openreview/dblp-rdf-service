from dataclasses import asdict
import click
from rich.pretty import pprint
from dblp_service.lib.log import create_logger

from dblp_service.open_exchange.open_fetch import fetch_notes_for_author, fetch_profile
from dblp_service.services.author_alignment import DblpAuthID, OpenreviewFetcher

from .cli import cli

log = create_logger(__file__)


@cli.group()
def openreview():
    """Query Jena (RDF DB)"""


@openreview.command()
@click.argument('id', type=str)
def profile(id: str):
    """Fetch (by id) and display a user profile from OpenReview"""
    profile = fetch_profile(id)
    if profile:
        pprint(asdict(profile))
        print("Notes==================")
        for note in fetch_notes_for_author(id):
            pprint(asdict(note))

    else:
        print('No Profile found')

@openreview.command()
@click.argument('id', type=str)
def dblp_profile(id: str):
    """"""
    fetch = OpenreviewFetcher()
    fetch.fetch_profile(DblpAuthID(id))
