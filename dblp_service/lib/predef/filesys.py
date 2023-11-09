
import os
from typing import Tuple

def ensure_directory(path: str) -> Tuple[bool, str]:
    """
    Check if the given path is a directory. If it does not exist, create it.
    If it exists but is not a directory, report an error.

    :param path: The path to check or create.
    :return: A tuple containing a boolean indicating success, and a message.

    Example usage:
    > success, message = ensure_directory('some/directory/path')
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
