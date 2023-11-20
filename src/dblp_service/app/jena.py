"""Manage Apache Jena RDF loading/unloading

"""


from pprint import pprint

from dblp_service.app.arg_helpers import zero_or_one
from .cli import cli, get_config
import click
from click.core import Context
import asyncio
import typing as t

from dblp_service.local_storage.jena_db import init_db


@cli.group()
def jena():
    """Manage Apache Jena RDF DB"""


@jena.command()
@click.pass_context
def init(ctx: Context):
    """Ensure that Jena is initialized"""
    assert (config := get_config(ctx))
    asyncio.run(init_db(config))


@jena.command('import')
@click.argument('md5-prefix', type=str, nargs=-1)
@click.pass_context
def import_rdfs(ctx: Context, md5_prefix: t.Tuple[str]):
    """Import RDFs into graphs, explicitly or stashed head/base by default"""
    provided, md5 = zero_or_one(md5_prefix)

    assert (config := get_config(ctx))

    if provided:
        pass
    pprint(config)


@jena.command()
@click.pass_context
def prune(ctx: Context):
    """Delete graphs from Jena, by MD5 ID or all but head/base by default"""
    assert (config := get_config(ctx))
    pprint(config)


@jena.command()
@click.pass_context
def report(ctx: Context):
    """Import RDFs from stash, explicit or head/base by default"""
    assert (config := get_config(ctx))
    pprint(config)
