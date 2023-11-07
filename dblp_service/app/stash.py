from app.cli import cli, get_config
import click
from click.core import Context

from dblp_service.rdfdb.file_stash import create_or_update_stash


@cli.group()
def stash():
    """Manage downloaded rdf db files"""


@stash.command()
@click.pass_context
def update(ctx: Context):
    """Create or update stash; fetch updated list of available files from dblp.org"""
    assert (config := get_config(ctx))
    create_or_update_stash(config)


@stash.command()
@click.pass_context
def report(ctx: Context):
    """Show available, downloaded, and imported files"""
    assert (config := get_config(ctx))


@stash.command()
@click.pass_context
@click.option("--revisions", type=int, default=1)
def download(ctx: Context):
    """Download and verify RDF files from dblp.org"""
    assert (config := get_config(ctx))


@stash.command("import")
@click.pass_context
def import_file(ctx: Context):
    """Import local file into stash"""
    assert (config := get_config(ctx))


# @stash.command()
# @click.option("--file", type=str, default=None)
# def download_rdf_file(file: t.Optional[str]):
#     """Fetch the latest RDF db file from https://dblp.org"""

#     download_and_verify_dblp_ttl()
