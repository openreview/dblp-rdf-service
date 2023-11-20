from contextlib import contextmanager
import io
import os

import typing as t


@contextmanager
def inplace(
    filename: str,
    mode: str = "r",
    buffering: int = -1,
    encoding: t.Optional[str] = None,
    errors: t.Optional[str]=None,
    newline: t.Optional[str] = None,
    backup_extension: t.Optional[str] = None,
):
    """Allow for a file to be replaced with new content.

    Taken from:
        https://www.zopatista.com/python/2013/11/26/inplace-file-rewriting/

    yields a tuple of (readable, writable) file objects, where writable
    replaces readable.

    If an exception occurs, the old file is restored, removing the
    written data.

    mode should *not* use 'w', 'a' or '+'; only read-only-modes are supported.

    """

    # move existing file to backup, create new file with same permissions
    # borrowed extensively from the fileinput module
    if set(mode).intersection("wa+"):
        raise ValueError("Only read-only file modes can be used")

    backupfilename = filename + (backup_extension or os.extsep + "bak")
    try:
        os.unlink(backupfilename)
    except os.error:
        pass
    os.rename(filename, backupfilename)
    readable = io.open(backupfilename, mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline)

    try:
        perm = os.fstat(readable.fileno()).st_mode
    except OSError:
        writable = open(
            filename,
            "w" + mode.replace("r", ""),
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
        )
    else:
        os_mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if hasattr(os, "O_BINARY"):
            os_mode |= os.O_BINARY
        fd = os.open(filename, os_mode, perm)
        writable = io.open(
            fd, "w" + mode.replace("r", ""), buffering=buffering, encoding=encoding, errors=errors, newline=newline
        )
        try:
            if hasattr(os, "chmod"):
                os.chmod(filename, perm)
        except OSError:
            pass
    try:
        yield readable, writable
    except Exception:
        # move backup back
        try:
            os.unlink(filename)
        except os.error:
            pass
        os.rename(backupfilename, filename)
        raise
    finally:
        readable.close()
        writable.close()
        try:
            os.unlink(backupfilename)
        except os.error:
            pass
