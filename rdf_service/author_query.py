from pprint import pprint
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import xml.etree.ElementTree as ET
import xml.dom.minidom


def query_author(authorURI: str):
    sparql = SPARQLWrapper(
        "http://localhost:3030/"
        "ds"
    )
    sparql.setReturnFormat(JSON)

    # sparql.setQuery("""
    #     prefix dblp: <https://dblp.org/rdf/schema#>

    #     SELECT ?pub ?pred ?obj ?bpred ?bobj
    #     WHERE {
    #       ?pub dblp:authoredBy """ f"<{authorURI}> ." """
    #       {  ?pub ?pred [ ?bpred ?bobj ] }
    #       UNION
    #       { ?pub ?pred ?obj }
    #     }
    #     ORDER BY ?pub ?pred
    #     """
    # )
    sparql.setQuery("""
        prefix dblp: <https://dblp.org/rdf/schema#>

        SELECT ?pub ?pred ?obj ?bpred ?bobj
        WHERE {
          ?pub dblp:authoredBy """ f"<{authorURI}> . " """
          {
            ?pub ?pred ?obj
            FILTER (! isBlank(?obj) )
          } UNION {
            ?pub ?pred ?obj
            FILTER (isBlank(?obj) ) .
            ?obj ?bpred ?bobj .
          }
        }
        """
    )

    def get_type_val(rec, key: str):
        if key not in rec:
            return None

        subrec = rec[key]
        t = subrec['type']
        v = subrec['value']
        return [t, v]

    try:
        ret = sparql.queryAndConvert()
        # pprint(ret)

        # root = ET.Element('root')
        for r in ret["results"]["bindings"]:
            # pprint(r)
            # body = ET.SubElement(root, 'triple', )
            pub = get_type_val(r, 'pub')
            pred  =get_type_val(r, "pred")
            obj   =get_type_val(r, "obj")
            bpred =get_type_val(r, "bpred")
            bobj  =get_type_val(r, "bobj")

            print(f"{pub}  {pred} {obj} [ {bpred} {bobj} ]")
    except Exception as e:
        print(e)



# with open('BodyUniversal.json') as f:
#     jsondata = json.load(f)

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

# print(pretty_xml)
# # <?xml version="1.0" ?>
# # <root>
# #         <Body>
# #                 <UniversalLiftSupport>
# #                         1&quot;-9&quot; Extended Length
# #                         10&quot;-14.5&quot; Extended Length
# #                         15&quot;-19&quot; Extended Length
# #                         20&quot; + Extended Length</UniversalLiftSupport>
# #         </Body>
# # </root>

# # OUTPUT XML CONTENT TO FILE
# with open('Output.xml','w') as f:
#     f.write(pretty_xml)

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
