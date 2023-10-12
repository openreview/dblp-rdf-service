#  <r>
#      <inproceedings key="conf/acl/ChangSRM23" mdate="2023-08-10">
#        <author pid="130/1022">Haw-Shiuan Chang</author>
#        <author pid="301/6251">Ruei-Yao Sun</author>
#        <author pid="331/1034">Kathryn Ricci</author>
#        <author pid="m/AndrewMcCallum">Andrew McCallum</author>
#        <title>Multi-CLS BERT: An Efficient Alternative to Traditional Ensembling.</title>
#        <pages>821-854</pages>
#        <year>2023</year>
#        <booktitle>ACL (1)</booktitle>
#        <ee type="oa">https://doi.org/10.18653/v1/2023.acl-long.48</ee>
#        <ee type="oa">https://aclanthology.org/2023.acl-long.48</ee>
#        <crossref>conf/acl/2023-1</crossref>
#        <url>db/conf/acl/acl2023-1.html#ChangSRM23</url>
#      </inproceedings>
#    </r>


from bigtree.tree.export import print_tree
from ..rdf_io.author_tree_transforms import (
    create_xml_root_elem,
    rewrite_authorship_tree,
    rewrite_hasSignature_node,
)

from ..rdf_io.xml_utils import print_xml

# from rdf_io.author_tree_transforms import  print_xml
from tests.helpers import get_author_tree, get_author_tree_from_string


def test_root_elem_creation():
    tuplestrs = ["('/DruckP12', '#bibtexType', '#Inproceedings')"]
    tree = get_author_tree(tuplestrs)
    xroot = create_xml_root_elem(tree)
    assert xroot.tag == "inproceedings"


def test_title_year_creation():
    tuples = """
        ('DruckP12', 'title', 'Title of the paper', )
        ('DruckP12', 'label', 'Author; Label of the paper', )
        ('DruckP12', 'yearOfPublication', '2012', )
        ('DruckP12', 'yearOfEvent', '2012', )
    """

    tree = get_author_tree_from_string(tuples)
    # xroot = create_xml_root_elem(tree)
    rewrite_authorship_tree(tree)
    # add_xml_elems(xroot, tree)
    # years = [e.text for e in xroot.findall("year")]

    # assert len(years) == 1
    # assert years[0] == "2012"


def test_signature_creation():
    tuples = """
        ('DruckP12', 'hasSignature', 'b5', 'signaturePublication', 'https://dblp.org/rec/conf/acl/DruckP12')
        ('DruckP12', 'hasSignature', 'b5', 'signatureDblpName', 'Gregory Druck')
        ('DruckP12', 'hasSignature', 'b5', 'signatureCreator', 'https://dblp.org/pid/66/4867')
        ('DruckP12', 'hasSignature', 'b5', 'signatureOrdinal', '1')
        ('DruckP12', 'hasSignature', 'b6', 'type', 'https://dblp.org/rdf/schema#AuthorSignature')
        ('DruckP12', 'hasSignature', 'b6', 'signaturePublication', 'https://dblp.org/rec/conf/acl/DruckP12')
        ('DruckP12', 'hasSignature', 'b6', 'signatureDblpName', 'Bo Pang')
        ('DruckP12', 'hasSignature', 'b6', 'signatureCreator', 'https://dblp.org/pid/16/6344')
        ('DruckP12', 'hasSignature', 'b6', 'signatureOrdinal', '2')
    """

    tree = get_author_tree_from_string(tuples)
    signature_node = tree.children[0]
    rewrite_hasSignature_node(signature_node)
    print_tree(signature_node, all_attrs=True)
    [elem1, elem2] = [sig.get_attr("element") for sig in signature_node.children]
    # TODO write assertions
    print_xml(elem1)
    print_xml(elem2)


def test_venue_creation():
    tuples = """
        ('DruckP12', 'publishedIn', 'ACL (1)', )
        ('DruckP12', 'publishedInBook', 'ACL (1)', )
        ('DruckP12', 'publishedAsPartOf', 'https://dblp.org/rec/conf/acl/2012-1', )
        ('DruckP12', 'pagination', '545-553', )
    """
    tree = get_author_tree_from_string(tuples)
    print_tree(tree, all_attrs=True)


# ('DruckP12', 'type', 'https://dblp.org/rdf/schema#Inproceedings', )
# ('DruckP12', 'type', 'https://dblp.org/rdf/schema#Publication', )
#
# ('DruckP12', 'publishedIn', 'ACL (1)', )
# ('DruckP12', 'publishedInBook', 'ACL (1)', )
# ('DruckP12', 'publishedAsPartOf', 'https://dblp.org/rec/conf/acl/2012-1', )
# ('DruckP12', 'pagination', '545-553', )
# ('DruckP12', 'listedOnTocPage', 'https://dblp.org/db/conf/acl/acl2012-1', )
# ('DruckP12', 'documentPage', 'https://aclanthology.org/P12-1057/', )
# ('DruckP12', 'primaryDocumentPage', 'https://aclanthology.org/P12-1057/', )
#
# ('DruckP12', 'numberOfCreators', '2', )
# ('DruckP12', 'authoredBy', 'https://dblp.org/pid/16/6344', )
# ('DruckP12', 'authoredBy', 'https://dblp.org/pid/66/4867', )
# ('DruckP12', 'yearOfPublication', '2012', )
# ('DruckP12', 'yearOfEvent', '2012', )
# ('DruckP12', 'bibtexType', 'http://purl.org/net/nknouf/ns/bibtex#Inproceedings', )
# ('DruckP12', 'title', 'Spice it up? Mining Refinements to Online Instructions from User Generated Content.', )
# ('DruckP12', 'label', 'Gregory Druck and Bo Pang: Spice it up? Mining Refinements to Online Instructions from User Generated Content. (2012)', )
# ('DruckP12', 'hasIdentifier', 'b4', 'type', 'http://purl.org/spar/datacite/ResourceIdentifier')
# ('DruckP12', 'hasIdentifier', 'b4', 'hasLiteralValue', 'conf/acl/DruckP12')
# ('DruckP12', 'hasIdentifier', 'b4', 'usesIdentifierScheme', 'http://purl.org/spar/datacite/dblp-record')
# ('DruckP12', 'hasSignature', 'b5', 'type', 'https://dblp.org/rdf/schema#AuthorSignature')
# ('DruckP12', 'hasSignature', 'b5', 'signaturePublication', 'https://dblp.org/rec/conf/acl/DruckP12')
# ('DruckP12', 'hasSignature', 'b5', 'signatureDblpName', 'Gregory Druck')
# ('DruckP12', 'hasSignature', 'b5', 'signatureCreator', 'https://dblp.org/pid/66/4867')
# ('DruckP12', 'hasSignature', 'b5', 'signatureOrdinal', '1')
# ('DruckP12', 'hasSignature', 'b6', 'type', 'https://dblp.org/rdf/schema#AuthorSignature')
# ('DruckP12', 'hasSignature', 'b6', 'signaturePublication', 'https://dblp.org/rec/conf/acl/DruckP12')
# ('DruckP12', 'hasSignature', 'b6', 'signatureDblpName', 'Bo Pang')
# ('DruckP12', 'hasSignature', 'b6', 'signatureCreator', 'https://dblp.org/pid/16/6344')
# ('DruckP12', 'hasSignature', 'b6', 'signatureOrdinal', '2')
