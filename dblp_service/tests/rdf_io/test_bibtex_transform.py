from dataclasses import dataclass
from bigtree.tree.export import print_tree
from bigtree.node.node import Node


from bibtexparser import Library, write_string, parse_string
from bibtexparser.middlewares.names import SeparateCoAuthors, MergeCoAuthors
from bibtexparser.middlewares import LatexEncodingMiddleware

from copy import copy, deepcopy
from textwrap import dedent

from bibtexparser.model import (
    Entry,
    ExplicitComment,
    Field,
    ImplicitComment,
    Preamble,
    String,
)

from rich.pretty import pprint

from dblp_service.rdf_io.bibtex_transform import apply_handlers_to_tree, output_to_bibtex
from dblp_service.tests.rdf_io.test_tupledata import AUTHOR_1_TUPLES, AUTHOR_2_TUPLES

from ..helpers import get_author_tree_from_string

@dataclass
class BibtexOutput:
    tree: Node
    tree_str: str
    entry: Entry
    bibtex_str: str


def tuplestr_to_bibtex_str(tuplestr: str) -> BibtexOutput:
    tree = get_author_tree_from_string(tuplestr)

    bibtex_entry = apply_handlers_to_tree(tree)
    library = Library()
    entry = output_to_bibtex(bibtex_entry)
    library.add(entry)
    bibtex_str = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )
    return BibtexOutput(
        tree = tree,
        tree_str='',
        entry = entry,
        bibtex_str=bibtex_str
    )



def test_tree_handler_dispatch():
    tuples = """
        ('DruckP12', 'x/schema#title', 'Title of the paper', )
        ('DruckP12', 'schema#label', 'Author; Label of the paper', )
        ('DruckP12', 'yearOfPublication', '2012', )
        ('DruckP12', 'foo/yearOfEvent', '2012', )
        ('DruckP12', "https://dblp.org/rdf/schema#bibtexType", "http://purl.org/net/nknouf/ns/bibtex#Inproceedings")
        ('DruckP12', "isA", "https://dblp.org/rdf/schema#Inproceedings")
        ('DruckP12', "isA", "https://dblp.org/rdf/schema#Publication")
    """

    bibout = tuplestr_to_bibtex_str(tuples)

    print(bibout.bibtex_str)


def test_bibtex_parsing():
    # author       = {Haw{-}Shiuan Chang and
    #                 Ruei{-}Yao Sun and
    #                 Kathryn Ricci and
    #                 Andrew McCallum},
    sample_bibtex = dedent(
        """

    @comment{
       Example Comment
    }

    @inproceedings{DBLP:conf/acl/ChangSRM23,
      author       = {Haw{-}Shiuan Chang},
      title        = {Multi-CLS {BERT:} An Efficient Alternative to Traditional Ensembling},
      booktitle    = {Proceedings of the 61st Annual Meeting of the Association for Computational
                      Linguistics (Volume 1: Long Papers), {ACL} 2023, Toronto, Canada,
                      July 9-14, 2023},
      pages        = {821--854},
      year         = {2023},
      crossref     = {DBLP:conf/acl/2023-1},
      url          = {https://doi.org/10.18653/v1/2023.acl-long.48},
      doi          = {10.18653/v1/2023.acl-long.48},
      timestamp    = {Thu, 10 Aug 2023 12:35:53 +0200},
      biburl       = {https://dblp.org/rec/conf/acl/ChangSRM23.bib},
      bibsource    = {dblp computer science bibliography, https://dblp.org}
    }
    """
    )
    bibtexLibrary = parse_string(
        sample_bibtex,
        append_middleware=[
            SeparateCoAuthors(allow_inplace_modification=True),
            # SplitNameParts(allow_inplace_modification=True),
        ],
    )
    # for entry in bibtexLibrary.blocks:
    #     print(f"== {entry}")

    for entry in bibtexLibrary.entries:
        print(f"== {entry}")
        for field in entry.fields:
            print(f"  > {field}")
            pprint(field.value)

    # print(write_string(bibtexLibrary))


def test_bibtex_construction():
    sample_bibtex = """
    @inproceedings{DBLP:conf/acl/ChangSRM23,
      author       = {Haw{-}Shiuan Chang and
                      Ruei{-}Yao Sun and
                      Kathryn Ricci and
                      Andrew McCallum},
      title        = {Multi-CLS {BERT:} An Efficient Alternative to Traditional Ensembling},
      booktitle    = {Proceedings of the 61st Annual Meeting of the Association for Computational
                      Linguistics (Volume 1: Long Papers), {ACL} 2023, Toronto, Canada,
                      July 9-14, 2023},
      pages        = {821--854},
      year         = {2023},
      crossref     = {DBLP:conf/acl/2023-1},
      url          = {https://doi.org/10.18653/v1/2023.acl-long.48},
      doi          = {10.18653/v1/2023.acl-long.48},
      timestamp    = {Thu, 10 Aug 2023 12:35:53 +0200},
      biburl       = {https://dblp.org/rec/conf/acl/ChangSRM23.bib},
      bibsource    = {dblp computer science bibliography, https://dblp.org}
    }
    """

    library = Library()
    entry = Entry(
        "inproceedings",
        "DBLP:conf/acl/ChangSRM23",
        [
            Field("author", ["Haw-Shiuan Chang", "Adam Saunders"]),
            Field("editor", ["Andrew McCallum", "M. Knight"]),
            Field("title", "The title"),
        ],
    )
    library.add(entry)

    as_string = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )

    print(as_string)


def test_bibtex_elements():
    entry_1 = Entry(
        "article",
        "key",
        [Field("field", "value", 1)],
        1,
        "raw",
    )
    entry_2 = copy(entry_1)
    assert entry_1 == entry_2
    # Not equal to entry with different entry-type
    entry_3 = Entry(
        "book",
        "key",
        [Field("field", "value", 1)],
        1,
        "raw",
    )
    assert entry_1 != entry_3

    ## deepcopy
    entry_2 = deepcopy(entry_1)
    assert entry_1 == entry_2

    string_1 = String(
        "key",
        "value",
        1,
        "raw",
    )
    assert string_1 == string_1

    preamble_1 = Preamble("value", 1, "raw")
    assert preamble_1 == preamble_1
    # Equal to identical preamble
    preamble_2 = Preamble("value", 1, "raw")
    assert preamble_1 == preamble_2

    comment_1 = ImplicitComment(start_line=1, comment="This is my comment", raw="#  This is my comment")

    comment_1 = ExplicitComment(start_line=1, comment="This is my comment", raw="#  This is my comment")

    string = String("myKey", "myValue", 1, "raw")
    assert str(string) == "String (line: 1, key: `myKey`): `myValue`"

    preamble = Preamble("myValue", 1)
    assert str(preamble) == "Preamble (line: 1): `myValue`"


def test_druck_has_signature():
    tuples = AUTHOR_1_TUPLES

    tree = get_author_tree_from_string(tuples)
    print_tree(tree)

    bibtex_entry = apply_handlers_to_tree(tree)
    entry = output_to_bibtex(bibtex_entry)

    library = Library()
    library.add(entry)
    as_string = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )

    print(as_string)


def test_druck_gg11():
    tuples = f"""
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#publishedIn', obj='ACL (Tutorial Abstracts)', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', obj='https://dblp.org/rdf/schema#Inproceedings', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', obj='https://dblp.org/rdf/schema#Publication', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#listedOnTocPage', obj='https://dblp.org/db/conf/acl/acl2011t', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#numberOfCreators', obj='3', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#publishedInBook', obj='ACL (Tutorial Abstracts)', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#pagination', obj='5', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#yearOfPublication', obj='2011', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#publishedAsPartOf', obj='https://dblp.org/rec/conf/acl/2011t', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#authoredBy', obj='https://dblp.org/pid/99/2806', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#authoredBy', obj='https://dblp.org/pid/66/4867', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#authoredBy', obj='https://dblp.org/pid/43/5339', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#yearOfEvent', obj='2011', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#bibtexType', obj='http://purl.org/net/nknouf/ns/bibtex#Inproceedings', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#title', obj='Rich Prior Knowledge in Learning for Natural Language Processing.', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://www.w3.org/2000/01/rdf-schema#label', obj='Gregory Druck et al.: Rich Prior Knowledge in Learning for Natural Language Processing. (2011)', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#documentPage', obj='https://aclanthology.org/P11-5005/', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#primaryDocumentPage', obj='https://aclanthology.org/P11-5005/', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='http://purl.org/spar/datacite/ResourceIdentifier')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='http://purl.org/spar/literal/hasLiteralValue', bobj='conf/acl/DruckGG11')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='http://purl.org/spar/datacite/usesIdentifierScheme', bobj='http://purl.org/spar/datacite/dblp-record')
        {AUTHOR_1_TUPLES}
        {AUTHOR_2_TUPLES}
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='https://dblp.org/rdf/schema#AuthorSignature')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signaturePublication', bobj='https://dblp.org/rec/conf/acl/DruckGG11')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signatureDblpName', bobj='João Graça')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signatureCreator', bobj='https://dblp.org/pid/99/2806')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signatureOrdinal', bobj='3')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='isA', obj='https://dblp.org/rdf/schema#Inproceedings', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='isA', obj='https://dblp.org/rdf/schema#Publication', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='isA', bobj='http://purl.org/spar/datacite/ResourceIdentifier')
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    """

    tree = get_author_tree_from_string(tuples)

    bibtex_entry = apply_handlers_to_tree(tree)
    entry = output_to_bibtex(bibtex_entry)
    library = Library()

    library.add(entry)
    as_string = write_string(
        library,
        prepend_middleware=[
            LatexEncodingMiddleware(allow_inplace_modification=True),
            MergeCoAuthors(allow_inplace_modification=True),
        ],
    )

    print(as_string)
