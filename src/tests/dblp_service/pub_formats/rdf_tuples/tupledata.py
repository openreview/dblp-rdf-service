"""Testing data for dblp and bibtex construction from RDF.
"""

from textwrap import dedent
from dblp_service.pub_formats.rdf_tuples.dblp_repr import DblpRepr
from dblp_service.pub_formats.rdf_tuples.tree_traversal import authorship_tree_to_dblp_repr

from tests.helpers import get_author_tree_from_string

DRUCK_BIBTEX_ENTRY = dedent(
    """
        @inproceedings{DBLP:conf/acl/DruckGG11,
          author       = {Gregory Druck and
                          Kuzman Ganchev and
                          Jo{\\~{a}}o Gra{\\c{c}}a},
          title        = {Rich Prior Knowledge in Learning for Natural Language Processing.},
          booktitle    = {The 49th Annual Meeting of the Association for Computational Linguistics:
                          Human Language Technologies, Proceedings of the Conference, 19-24
                          June, 2011, Portland, Oregon, {USA} - Tutorial Abstracts},
          pages        = {5},
          year         = {2011},
          crossref     = {DBLP:conf/acl/2011t},
          url          = {https://aclanthology.org/P11-5005/},
          timestamp    = {Fri, 06 Aug 2021 00:40:56 +0200},
          biburl       = {https://dblp.org/rec/conf/acl/DruckGG11.bib},
          bibsource    = {dblp computer science bibliography, https://dblp.org}
        }
"""
)

# The RDF tuples for author 'Gregory Druck'
AUTHOR_1_TUPLES = dedent(
    """
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signaturePublication', bobj='https://dblp.org/rec/conf/acl/DruckGG11')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signatureDblpName', bobj='Gregory Druck')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signatureCreator', bobj='https://dblp.org/pid/66/4867')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signatureOrdinal', bobj='1')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
"""
)

# The RDF tuples for author 'Kuzman Ganchev'
AUTHOR_2_TUPLES = dedent(
    """
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signaturePublication', bobj='https://dblp.org/rec/conf/acl/DruckGG11')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signatureDblpName', bobj='Kuzman Ganchev')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signatureCreator', bobj='https://dblp.org/pid/43/5339')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signatureOrdinal', bobj='2')
"""
)

# The RDF tuples for author 'João Graça'
AUTHOR_3_TUPLES = dedent(
    """
     ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='https://dblp.org/rdf/schema#AuthorSignature')
     ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signaturePublication', bobj='https://dblp.org/rec/conf/acl/DruckGG11')
     ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signatureDblpName', bobj='João Graça')
     ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signatureCreator', bobj='https://dblp.org/pid/99/2806')
     ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='https://dblp.org/rdf/schema#signatureOrdinal', bobj='3')
     ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b10', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    """
)

# RDF tuples specifying author count and dblp.org pids
AUTHOR_ID_TUPLES = dedent(
    """
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#numberOfCreators', obj='3', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#authoredBy', obj='https://dblp.org/pid/99/2806', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#authoredBy', obj='https://dblp.org/pid/66/4867', bpred=None, bobj=None)
        ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#authoredBy', obj='https://dblp.org/pid/43/5339', bpred=None, bobj=None)
    """
)

# RDF tuples for title, year, journal, and others.
TITLE_VENUE_TUPLES = dedent(
    """
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#publishedIn', obj='ACL (Tutorial Abstracts)', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#listedOnTocPage', obj='https://dblp.org/db/conf/acl/acl2011t', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#publishedInBook', obj='ACL (Tutorial Abstracts)', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#pagination', obj='5', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#yearOfPublication', obj='2011', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#publishedAsPartOf', obj='https://dblp.org/rec/conf/acl/2011t', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#yearOfEvent', obj='2011', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#title', obj='Rich Prior Knowledge in Learning for Natural Language Processing.', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://www.w3.org/2000/01/rdf-schema#label', obj='Gregory Druck et al.: Rich Prior Knowledge in Learning for Natural Language Processing. (2011)', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#documentPage', obj='https://aclanthology.org/P11-5005/', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#primaryDocumentPage', obj='https://aclanthology.org/P11-5005/', bpred=None, bobj=None)
    """
)

# Tuple data used to define publication type e.g., @inproceedings|@article|@book/etc.{
PUBLICATION_ID_TUPLES = dedent(
    """
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#bibtexType', obj='http://purl.org/net/nknouf/ns/bibtex#Inproceedings', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', obj='https://dblp.org/rdf/schema#Inproceedings', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', obj='https://dblp.org/rdf/schema#Publication', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='isA', obj='https://dblp.org/rdf/schema#Inproceedings', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='isA', obj='https://dblp.org/rdf/schema#Publication', bpred=None, bobj=None)
    """
)

# Tuple data used to define key e.g., @...{DBLP:conf/acl/DruckGG11
RESOURCE_IDENTIFIER_TUPLES = dedent(
    """
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='http://purl.org/spar/datacite/ResourceIdentifier')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='http://purl.org/spar/literal/hasLiteralValue', bobj='conf/acl/DruckGG11')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='http://purl.org/spar/datacite/usesIdentifierScheme', bobj='http://purl.org/spar/datacite/dblp-record')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='http://purl.org/spar/datacite/hasIdentifier', obj='b7', bpred='isA', bobj='http://purl.org/spar/datacite/ResourceIdentifier')
    """
)

# The tree representation for author "Gregory Druck"
AUTHOR_1_TREE = dedent(
    """
    https://dblp.org/rec/conf/acl/DruckGG11
    ├── https://dblp.org/rdf/schema#hasSignature
    │   └── b8
    │       ├── http://www.w3.org/1999/02/22-rdf-syntax-ns#type
    │       │   └── https://dblp.org/rdf/schema#AuthorSignature
    │       ├── https://dblp.org/rdf/schema#signaturePublication
    │       │   └── https://dblp.org/rec/conf/acl/DruckGG11
    │       ├── https://dblp.org/rdf/schema#signatureDblpName
    │       │   └── Gregory Druck
    │       ├── https://dblp.org/rdf/schema#signatureCreator
    │       │   └── https://dblp.org/pid/66/4867
    │       ├── https://dblp.org/rdf/schema#signatureOrdinal
    │       │   └── 1
    │       └── isA
    │           └── https://dblp.org/rdf/schema#AuthorSignature
    └── isA
        ├── https://dblp.org/rdf/schema#Inproceedings
        └── https://dblp.org/rdf/schema#Publication
"""
)

def load_repr_sample() -> DblpRepr:
    tuples = f"""
    {PUBLICATION_ID_TUPLES}
    {RESOURCE_IDENTIFIER_TUPLES}
    {TITLE_VENUE_TUPLES}
    {AUTHOR_1_TUPLES}
    {AUTHOR_2_TUPLES}
    {AUTHOR_3_TUPLES}
    {AUTHOR_ID_TUPLES}
    """

    tree = get_author_tree_from_string(tuples)
    return authorship_tree_to_dblp_repr(tree, step_debug=False)
