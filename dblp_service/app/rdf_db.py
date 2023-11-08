from pprint import pprint
from .cli import cli, get_config
import click
from click.core import Context
import asyncio

from dblp_service.rdfdb.manage_db import init_db


@cli.group()
def rdf():
    """Manage Apache Jena RDF DB"""


@rdf.command()
@click.pass_context
@click.option("--init", is_flag=True, default=False)
@click.option("--clean", is_flag=True, default=False)
@click.option("--report", is_flag=True, default=False)
def db_manage(ctx: Context, init: bool, clean: bool, report: bool):
    """Init/clean/report on db"""
    assert (config := get_config(ctx))
    asyncio.run(init_db(config))


@rdf.command()
@click.pass_context
@click.option("--file", type=str)
@click.option("--graph", type=str)
def load_rdfs(ctx: Context, file: str, graph: str):
    print(f"load {file} into {graph}")
    assert (config := get_config(ctx))
    pprint(config)
    ## default to latest..


@rdf.command()
def rotate_dbs():
    print("rotate")
    ## default to latest..


@rdf.command()
@click.option("--graph1", type=str)
@click.option("--graph2", type=str)
def diff_dbs(graph1: str, graph2: str):
    print("diff")
