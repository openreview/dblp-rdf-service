import pytest


from dblp_service.local_storage.graph_naming import DblpGraphName, DiffGraphName, uri_to_graph_name


def test_ok_uri_to_graph_name():
    examples = [
        ('/g/abcd', DblpGraphName('abcd')),
        ('g/abcd', DblpGraphName('abcd')),
        ('g/abcd/', DblpGraphName('abcd')),
        ('/g/abcd/', DblpGraphName('abcd')),
        ('/diff/g/abcd/g/1234', DiffGraphName(DblpGraphName('abcd'), DblpGraphName('1234'))),
        ('/diff/g/abcd/g/1234/', DiffGraphName(DblpGraphName('abcd'), DblpGraphName('1234'))),
        ('diff/g/abcd/g/1234/', DiffGraphName(DblpGraphName('abcd'), DblpGraphName('1234'))),
    ]

    for [uri, gname] in examples:
        assert uri_to_graph_name(uri) == gname


def test_bad_uri_to_graph_name():
    examples = [
        '',
        'foo',
        '/foo',
        '/diff',
        '/diff/g',
        '/diff/g/',
    ]

    for uri in examples:
        with pytest.raises(Exception):
            uri_to_graph_name(uri)
