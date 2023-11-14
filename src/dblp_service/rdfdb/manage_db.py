from dblp_service.lib.predef.config import Config
from dblp_service.lib.predef.filesys import ensure_directory
from dblp_service.rdfdb.fuseki_context import FusekiServerManager


async def init_db(config: Config):
    """
    Ensure that db exists on filesys.
    Create if not.
    report on: location, env, existing graphs, tuple counts
    """
    dbloc = config.jena.dbLocation
    success, msg = ensure_directory(dbloc)
    print(msg)
    if not success:
        print("could not initialize db")
        return

    async with FusekiServerManager(db_location=dbloc):
        pass
