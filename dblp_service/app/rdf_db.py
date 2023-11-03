from app.cli import cli
from dblp_service.rdfdb.update_db import download_and_verify_dblp_ttl


@cli.group()
def rdf():
    """Manage Apache Jena (RDF DB)"""


@rdf.command()
def download_db():
    download_and_verify_dblp_ttl()


@rdf.command()
def load_dblp_db():
    print("load")
    ## default to latest..


@rdf.command()
def rotate_dbs():
    print("rotate")
    ## default to latest..


@rdf.command()
def diff_dbs():
    print("diff")


