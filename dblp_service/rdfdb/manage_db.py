import os
from typing import Tuple

from dblp_service.lib.predef.config import Config
from dblp_service.rdfdb.fuseki_context import FusekiServerManager


def ensure_directory_path(path: str) -> Tuple[bool, str]:
    """
    Check if the given path is a directory. If it does not exist, create it.
    If it exists but is not a directory, report an error.

    :param path: The path to check or create.
    :return: A tuple containing a boolean indicating success, and a message.

    Example usage:
    > success, message = check_or_create_directory('some/directory/path')
    > print(message)
    """
    if os.path.exists(path):
        if os.path.isdir(path):
            return True, f"The path '{path}' is a directory."
        else:
            return False, f"Error: The path '{path}' exists but is not a directory."
    else:
        try:
            os.makedirs(path)
            return True, f"The directory '{path}' has been created."
        except OSError as e:
            return False, f"Error: The directory '{path}' could not be created. {e}"


async def init_db(config: Config):
    """
    Ensure that db exists on filesys.
    Create if not.
    report on: location, env, existing graphs, tuple counts
    """
    dbloc = config.jena.dbLocation
    success, msg = ensure_directory_path(dbloc)
    print(msg)
    if not success:
        print("could not initialize db")
        return

    async with FusekiServerManager(db_location=dbloc):
        pass
