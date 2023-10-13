from bigtree.tree.export import print_tree

# from bibtexparser.bibdatabase import BibDatabase
# from bibtexparser.model import

from dblp_service.rdf_io.bibtex_transform import apply_handlers_to_tree

from ..helpers import get_author_tree_from_string


def test_tree_handler_dispatch():
    tuples = """
        ('DruckP12', 'x/schema#title', 'Title of the paper', )
        ('DruckP12', 'schema#label', 'Author; Label of the paper', )
        ('DruckP12', 'yearOfPublication', '2012', )
        ('DruckP12', 'foo/yearOfEvent', '2012', )
        ('DruckP12', "https://dblp.org/rdf/schema#bibtexType", "http://purl.org/net/nknouf/ns/bibtex#Inproceedings")
    """

    tree = get_author_tree_from_string(tuples)
    print_tree(tree)

    for node in tree.children:
        apply_handlers_to_tree(node)
