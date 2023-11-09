
from dblp_service.app.arg_helpers import zero_or_one
from .cli import cli, get_config
import click
from click.core import Context
import typing as t

from dblp_service.rdfdb.file_stash import (
    create_or_update_stash,
    create_stash_report,
    set_base_and_head,
)


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
    report = create_stash_report(config)
    print(report)


@stash.command()
@click.pass_context
@click.argument("md5-prefix", type=str, nargs=-1)
def download(ctx: Context):
    """Download and verify RDF files from dblp.org.

    Downloads  RDFs  for  base  and  head versions,  if  they  are  not  already
    downloaded
    """
    assert (config := get_config(ctx))
    # download_and_verify_dblp_ttl()


@stash.command("import")
@click.pass_context
def import_file(ctx: Context):
    """Import local file into stash"""
    assert (config := get_config(ctx))



@stash.command()
@click.pass_context
@click.argument("md5-prefix", type=str, nargs=-1)
def set_base(ctx: Context, md5_prefix: t.Tuple[str]):
    """Set the ID of the export to use  as the base (older) version. If no ID is
    specified, defaults to second most recent available export.
    """
    assert (config := get_config(ctx))

    success, md5 = zero_or_one(md5_prefix)

    if success:
        set_base_and_head(config, md5=md5, set_base=True)
        print(create_stash_report(config))


@stash.command()
@click.pass_context
@click.argument("md5-prefix", type=str, nargs=-1)
def set_head(ctx: Context, md5_prefix: t.Tuple[str]):
    """Set the ID of the export to use  as the head (newer) version. If no ID is
    specified, defaults to the most recent available export.
    """
    assert (config := get_config(ctx))

    success, md5 = zero_or_one(md5_prefix)

    if success:
        set_base_and_head(config, md5=md5, set_head=True)

        print(create_stash_report(config))


# @stash.command()
# @click.option("--file", type=str, default=None)
# def download_rdf_file(file: t.Optional[str]):
#     """Fetch the latest RDF db file from https://dblp.org"""

#     download_and_verify_dblp_ttl()
