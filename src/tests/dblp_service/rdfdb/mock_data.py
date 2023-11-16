from dataclasses import replace
from itertools import islice
import tempfile
import typing as t
from contextlib import contextmanager

from dblp_service.lib.predef.config import load_config
from dblp_service.rdfdb.file_stash_manager import (
    FileStash,
    StashIndex,
)

from dblp_service.rdfdb.dblp_rdf_catalog import (
    DblpRdfCatalog,
    DblpRdfFile,
)
from random import choice
import collections

most_recent_rdf_file = DblpRdfFile(filename='dblp.nt.gz', md5='0ba5a47ff1d882686b2e9553a886739c')


timestamped_rdf_files = [
    DblpRdfFile(filename='dblp-2023-11-03.nt.gz', md5='88cc90ebdd04bac3cdf72bf1ac878b58'),
    DblpRdfFile(filename='dblp-2023-10-01.nt.gz', md5='4aa22d6b038ceef3849a7423fcf15365'),
    DblpRdfFile(filename='dblp-2023-09-01.nt.gz', md5='572661d887a04191893bb29beef61768'),
    DblpRdfFile(filename='dblp-2023-08-01.nt.gz', md5='1a97d3506208d99592be9ade9012763b'),
    DblpRdfFile(filename='dblp-2023-07-03.nt.gz', md5='6bc3587d2af5c39b72e664baed29d3b5'),
]

timestamped_rdf_md5s = [f.md5 for f in timestamped_rdf_files]
html_links = [f"<a href='{f.filename}'> {f.filename} </a>" for f in timestamped_rdf_files]


def gen_md5(i: int) -> str:
    choices = [str(x) for x in [*range(10), *'abcedf']]
    tail = ''.join(choice(choices) for _ in range(19))
    return f'{i}{tail}'


def gen_md5s(n: int) -> t.List[str]:
    return [gen_md5(i) for i in range(n)]


A = t.TypeVar('A')


def sliding_window(iterable: t.Iterable[A], n: int) -> t.Generator[t.List[A], t.Any, t.Any]:
    # sliding_window('ABCDEFG', 4) --> ABCD BCDE CDEF DEFG
    it = iter(iterable)
    window = collections.deque(islice(it, n), maxlen=n)
    if len(window) == n:
        yield list(window)
    for x in it:
        window.append(x)
        yield list(window)


def rolling_catalogs() -> t.Generator[DblpRdfCatalog, t.Any, t.Any]:
    rdf_files = [DblpRdfFile(filename=f'dblp-2023-0{i}-03.nt.gz', md5=md5) for i, md5 in enumerate(gen_md5s(8))]
    file_windows = sliding_window(rdf_files, 4)
    for filewin in file_windows:
        files = list(filewin[:])
        files[0] = replace(files[0], filename='dblp.nt.gz')
        catalog = DblpRdfCatalog(latest_release=files[0], archived_releases=files[1:])
        yield catalog


@contextmanager
def test_file_stash(catalog: t.Optional[DblpRdfCatalog] = None) -> t.Generator[FileStash, t.Any, t.Any]:
    assert (config := load_config())
    with tempfile.TemporaryDirectory() as tmpdirname:
        config.dblpServiceRoot = tmpdirname
        file_stash = FileStash(config)
        file_stash.ensure_dirs()

        if catalog:
            stash_index = StashIndex.from_catalog(catalog)
            file_stash.write_index(stash_index)

        yield file_stash
