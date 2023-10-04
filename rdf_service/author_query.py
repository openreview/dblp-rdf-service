import bigtree as bt
import typing as t
from bigtree.node.node import Node
from bigtree.tree.export import print_tree
from bigtree.tree.construct import add_path_to_tree
from rdf_service.queries import run_query
import xml.etree.ElementTree as ET
import xml.dom.minidom

from rdf_service.trees import Tree, tree_get_str, tree_path_exists, tree_get_tree
from rich import print


def signature_to_xml(tree: Tree):
    pass


def uri_last_path(s: str) -> str:
    if not s:
        return ""
    if s.startswith("http"):
        sp = s.split("/")
        return sp[-1]
    return s


rdf_to_xml_mapping = {
    "dblp": {
        "publishedIn": "",
        "publishedInJournal": "",
        "publishedInJournalVolume": "",
        "yearOfPublication": "",
        "title": "",
        "bibtexType": "",
        "documentPage": "",
        "primaryDocumentPage": "",
    }
}


def reduce_tree_nodes(tree: Tree):
    for maybe_key in tree.children:
        # if child has 1 child, reduce to attr child.name=child.child.name
        if len(maybe_key.children) == 1 and len(maybe_key.children[0].children) == 0:
            key_node = maybe_key
            value_node = maybe_key.children[0]
            ## strip leading http://../..
            attrvalue = uri_last_path(value_node.node_name) or value_node.node_name

            key_node.set_attrs(dict([["type", "attr"], ["value", attrvalue]]))
            value_node.parent = None # type: ignore


def get_matching_attr(node: Tree, keypat: str) -> t.Optional[str]:
    for attr_node in node.children:
        if attr_node.get_attr("type") != "attr":
            continue
        attr_name = attr_node.node_name.lower()
        if attr_name.endswith(keypat.lower()):
            return attr_node.get_attr("value")


def has_matching_attr(node: Tree, keypat: str, valpat: str) -> bool:
    attr_value = get_matching_attr(node, keypat)
    if not attr_value:
        return False

    return attr_value.lower().endswith(valpat.lower())


def create_xml_root_elem(node: Tree):
    if has_matching_attr(node, "bibtexType", "InProceedings"):
        return ET.Element("inproceedings")

    return ET.Element("article-todo")


def add_xml_elems(xroot: ET.Element, node: Tree):
    def year_elem():
        attr = get_matching_attr(node, "yearOfPublication")
        if not attr:
            return None
        elem = ET.Element("year")
        elem.text = attr
        return elem

    year = year_elem()
    if year is not None:
        xroot.append(year)
        print_xml(xroot)


def tree_to_xml(root: Tree):
    for node in root.children:
        reduce_tree_nodes(node)
        xml_root = create_xml_root_elem(node)
        add_xml_elems(xml_root, node)
        print_tree(node, all_attrs=True)
        print_xml(xml_root)


def print_xml(root: ET.Element):
    tree_out = ET.tostring(root, encoding="UTF-8")
    newXML = xml.dom.minidom.parseString(tree_out.decode("UTF-8"))
    pretty_xml = newXML.toprettyxml()
    print(pretty_xml)


def query_author(authorURI: str) -> Node:
    sep = "|"
    tuples = run_query(authorURI)
    root: Tree = Node("root")
    for tuple in tuples:
        path = sep.join(["root"] + [p for p in tuple if p])
        add_path_to_tree(root, path=path, sep=sep)

    tree_to_xml(root)

    return root


# with open('BodyUniversal.json') as f:
#     jsondata = json.load(f)

# import xml.etree.ElementTree as ET
# import xml.dom.minidom
# INITIALIZING XML DOC AND PARENT TAGS
# root = ET.Element('root')
# body = ET.SubElement(root, 'Body')
# uls = ET.SubElement(body, 'UniversalLiftSupport')
# uls.text = ''

# # ITERATE THROUGH LIST, APPENDING TO XML
# for i in jsondata[0]['Body'][0]['Universal Lift Support']:
#     uls.text = uls.text + '\n\t\t\t' + i

# # OUTPUT AND PRETTY PRINT TREE
# tree_out = ET.tostring(root, encoding="UTF-8")
# newXML = xml.dom.minidom.parseString(tree_out.decode('UTF-8'))
# pretty_xml = newXML.toprettyxml()


# prefix xsd: <http://www.w3.org/2001/XMLSchema#>
# prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
# prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# prefix owl: <http://www.w3.org/2002/07/owl#>
# prefix bf: <http://id.loc.gov/ontologies/bibframe/>
# prefix bibo: <http://purl.org/ontology/bibo/>
# prefix bibtex: <http://purl.org/net/nknouf/ns/bibtex#>
# prefix cito: <http://purl.org/spar/cito/>
# prefix datacite: <http://purl.org/spar/datacite/>
# prefix dbo: <http://dbpedia.org/ontology/>
# prefix dc: <http://purl.org/dc/elements/1.1/>
# prefix dct: <http://purl.org/dc/terms/>
# prefix foaf: <http://xmlns.com/foaf/0.1/>
# prefix litre: <http://purl.org/spar/literal/>
# prefix locid: <http://id.loc.gov/vocabulary/identifiers/>
# prefix locrel: <http://id.loc.gov/vocabulary/relators/>
# prefix schema: <https://schema.org/>
# prefix wd: <http://www.wikidata.org/entity/>
# prefix wdt: <http://www.wikidata.org/prop/direct/>
