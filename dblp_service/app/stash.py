from dblp_service.app.arg_helpers import zero_or_one
from dblp_service.lib.predef.log import create_logger
from dblp_service.rdfdb.file_stash_manager import FileStash
from .cli import cli, get_config
import click
from click.core import Context
import typing as t

log = create_logger(__file__)

@cli.group()
def stash():
    """Manage downloaded rdf db files"""


@stash.command()
@click.pass_context
def update(ctx: Context):
    """Create or update stash; fetch updated list of available files from dblp.org"""
    assert (config := get_config(ctx))
    fstash = FileStash(config)
    fstash.create_or_update()


@stash.command()
@click.pass_context
def report(ctx: Context):
    """Show available, downloaded, and imported files"""
    assert (config := get_config(ctx))
    fstash = FileStash(config)
    print(fstash.create_report())


@stash.command()
@click.pass_context
@click.argument("md5-prefix", type=str, nargs=-1)
def download(ctx: Context):
    """Download and verify RDF files from dblp.org.

    Downloads  RDFs  for  base  and  head versions,  if  they  are  not  already
    downloaded
    """
    assert (config := get_config(ctx))
    fstash = FileStash(config)
    # download_and_verify_dblp_ttl()


@stash.command("import")
@click.pass_context
@click.argument("filename", type=click.Path(exists=True, file_okay=True, dir_okay=False))
def import_file(ctx: Context, filename: str):
    """Import local file into stash"""
    assert (config := get_config(ctx))
    fstash = FileStash(config)

    fstash.import_file(filename)
    fstash.get_imported_files()

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
        fstash = FileStash(config)
        fstash.set_base_version(md5)
        print(fstash.create_report())


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
        fstash = FileStash(config)
        fstash.set_head_version(md5)
        print(fstash.create_report())
