"""Create a bibtex-style representation from an RDF-derived tree.
"""

import typing as t
import xml.etree.ElementTree as ET
from bigtree import Node  # type: ignore
from bigtree.utils.iterators import preorder_iter, postorder_iter

from .trees import (
    get_elem,
    has_elem,
)


def authorship_tree_to_bibtex(root: Node) -> ET.Element:
    """ """
    for n in preorder_iter(root, has_elem):
        if n.depth == 1:
            continue

        elem = get_elem(n)
        assert elem is not None

        containing_elems = [get_elem(a) for a in n.ancestors if has_elem(a)]

        nearest_elem = containing_elems[0]
        assert nearest_elem is not None
        nearest_elem.append(elem)

    rootelem = get_elem(root)
    assert rootelem is not None
    return rootelem



def apply_handlers_to_tree(root: Node):
    classHandlers = BibTexClassNodeHandlers()
    propHandlers = BibTexEntityPropertyHandlers()
    print(f"root.depth={root.depth}")
    for node in postorder_iter(root):
        relative_depth = (node.depth - root.depth) + 2
        print(f"visiting> node({node.node_name}); depth={node.depth} rel_depth={relative_depth} ")
        if relative_depth == 3:
            relation = node.parent
            assert relation is not None
            subject = relation.parent
            assert subject is not None
            subj = subject.node_name
            rel = relation.node_name
            rel_end = rel.split("/")[-1]
            if "#" in rel_end:
                rel_end = rel_end.split("#")[-1]
            obj = node.node_name
            print(f"{subj} -[{rel_end}] -> {obj}")

            do = f"hasA_{rel_end}"
            print(f"looking for handler `{do}`")
            if hasattr(propHandlers, do) and callable(func := getattr(propHandlers, do)):
                print(f"Calling {do}")
                func(subject, obj)


class BibTexClassNodeHandlers:
    """Classes Derived from dblp/schema.rdf"""

    def isA_Entity(self, entity: Node):
        """A general, identifiable entity in dblp."""
        pass

    def isA_Creator(self, entity: Node):
        """A creator of a publication."""
        pass

    def isA_AmbiguousCreator(self, entity: Node):
        """Not an actual creator, but an ambiguous proxy for an unknown number of unrelated actual creators. Associated publications do not have their true creators determined yet."""
        pass

    def isA_Person(self, entity: Node):
        """An actual person, who is a creator of a publication."""
        pass

    def isA_Group(self, entity: Node):
        """A creator alias used by a group or consortium of persons."""
        pass

    def isA_Signature(self, entity: Node):
        """The information that links a publication to a creator."""
        pass

    def isA_AuthorSignature(self, entity: Node):
        """The information that links a publication to an author."""
        pass

    def isA_EditorSignature(self, entity: Node):
        """The information that links a publication to an editor."""
        pass

    def isA_Publication(self, entity: Node):
        """A publication."""
        pass

    def isA_Book(self, entity: Node):
        """A book or a thesis."""
        pass

    def isA_Article(self, entity: Node):
        """A journal article."""
        pass

    def isA_Inproceedings(self, entity: Node):
        """A conference or workshop paper."""
        pass

    def isA_Incollection(self, entity: Node):
        """A part/chapter in a book or a collection."""
        pass

    def isA_Editorship(self, entity: Node):
        """An edited publication."""
        pass

    def isA_Reference(self, entity: Node):
        """A reference work entry."""
        pass

    def isA_Data(self, entity: Node):
        """Research data or artifacts."""
        pass

    def isA_Informal(self, entity: Node):
        """An informal or other publication."""
        pass

    def isA_Withdrawn(self, entity: Node):
        """A withdrawn publication item."""
        pass


class BibTexEntityPropertyHandlers:
    """Properties Derived from dblp/schema.rdf"""

    def hasA_identifier(self, entity: Node, value: Node):
        """An abstract identifier."""
        pass

    def hasA_wikidata(self, entity: Node, value: Node):
        """A wikidata item."""
        pass

    def hasA_webpage(self, entity: Node, value: Node):
        """The URL of a web page about this item."""
        pass

    def hasA_archivedWebpage(self, entity: Node, value: Node):
        """The URL of an archived web page about this item, which may no longer be available in the web."""
        pass

    def hasA_wikipedia(self, entity: Node, value: Node):
        """The URL of an (English) Wikipedia article about this item."""
        pass

    def hasA_orcid(self, entity: Node, value: Node):
        """An Open Researcher and Contributor ID."""
        pass

    def hasA_creatorName(self, entity: Node, value: Node):
        """The full name of the creator."""
        pass

    def hasA_primaryCreatorName(self, entity: Node, value: Node):
        """The primary full name of the creator."""
        pass

    def hasA_creatorNote(self, entity: Node, value: Node):
        """An additional note about the creator."""
        pass

    def hasA_affiliation(self, entity: Node, value: Node):
        """A (past or present) affiliation of the creator. (Remark: This
        property currently just gives literal xsd:string values until
        institutions are modelled as proper entities.
        """
        pass

    def hasA_primaryAffiliation(self, entity: Node, value: Node):
        """The primary affiliation of the creator. (Remark: This property
        currently just gives literal xsd:string values until institutions are
        modelled as proper entities.)
        """
        pass

    def hasA_awardWebpage(self, entity: Node, value: Node):
        """The URL of a web page about an award received by this creator."""
        pass

    def hasA_homepage(self, entity: Node, value: Node):
        """The URL of an academic homepage of this creator."""
        pass

    def hasA_primaryHomepage(self, entity: Node, value: Node):
        """The primary URL of an academic homepage of this creator."""
        pass

    def hasA_creatorOf(self, entity: Node, value: Node):
        """The creator of the publication."""
        pass

    def hasA_authorOf(self, entity: Node, value: Node):
        """The creator is the author of the publication."""
        pass

    def hasA_editorOf(self, entity: Node, value: Node):
        """The creator is the editor of the publication."""
        pass

    def hasA_coCreatorWith(self, entity: Node, value: Node):
        """The creator is co-creator with the other creator."""
        pass

    def hasA_coAuthorWith(self, entity: Node, value: Node):
        """The creator is co-author with the other creator."""
        pass

    def hasA_coEditorWith(self, entity: Node, value: Node):
        """The creator is co-editor with the other creator."""
        pass

    def hasA_homonymousCreator(self, entity: Node, value: Node):
        """This creator shares a homonymous name with the other creator."""
        pass

    def hasA_possibleActualCreator(self, entity: Node, value: Node):
        """This ambiguous creator may be (or may be not) just a disambiguation
        proxy for the other creator. Further actual creator candidates are
        possible.

        """
        pass

    def hasA_proxyAmbiguousCreator(self, entity: Node, value: Node):
        """This creator (and any of her fellow homonymous creators) is also
        represented by the given ambiguous creator in cases where the authorship
        of a publication is undetermined.

        """
        pass

    def hasA_signatureCreator(self, entity: Node, value: Node):
        """A linked creator of the publication."""
        pass

    def hasA_signatureDblpName(self, entity: Node, value: Node):
        """A dblp name (including any possible trailing homonym number) that links the publication to a creator."""
        pass

    def hasA_signatureOrcid(self, entity: Node, value: Node):
        """An ORCID that links the publication to a creator."""
        pass

    def hasA_signatureOrdinal(self, entity: Node, value: Node):
        """The ordinal number of this signature for the publication, starting with 1."""
        pass

    def hasA_signaturePublication(self, entity: Node, value: Node):
        """The publication of this signature."""
        pass

    def hasA_doi(self, entity: Node, value: Node):
        """A Digital Object Identifier."""
        pass

    def hasA_isbn(self, entity: Node, value: Node):
        """An International Standard Book Number."""
        pass

    def hasA_title(self, entity: Node, value: Node):
        """The title of the publication."""
        pass

    def hasA_bibtexType(self, entity: Node, value: Node):
        """The bibtex type of the publication, e.g. book, inproceedings, etc."""
        pass

    def hasA_createdBy(self, entity: Node, value: Node):
        """The publication is created by the creator."""
        pass

    def hasA_authoredBy(self, entity: Node, value: Node):
        """The publication is authored by the creator."""
        pass

    def hasA_editedBy(self, entity: Node, value: Node):
        """The publication is edited by the creator."""
        pass

    def hasA_numberOfCreators(self, entity: Node, value: Node):
        """The number of creators who created this publication."""
        pass

    def hasA_hasSignature(self, entity: Node, value: Node):
        """A signature that links this publication to an creator."""
        pass

    def hasA_documentPage(self, entity: Node, value: Node):
        """The URL of the electronic edition of the publication."""
        pass

    def hasA_primarydocumentPage(self, entity: Node, value: Node):
        """The primary URL of the electronic edition of the publication."""
        pass

    def hasA_listedOnTocPage(self, entity: Node, value: Node):
        """The url of the dblp table of contents page listing this publication."""
        pass

    def hasA_publishedIn(self, entity: Node, value: Node):
        """The name of the series, the journal, or the book in which the
        publication has been published. (Remark: This property currently just
        gives literal xsd:string values until journals and conference series are
        modelled as proper entities.)

        """
        pass

    def hasA_publishedInSeries(self, entity: Node, value: Node):
        """The name of the series in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInSeriesVolume(self, entity: Node, value: Node):
        """The volume of the series in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)"""
        pass

    def hasA_publishedInJournal(self, entity: Node, value: Node):
        """The name of the journal in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInJournalVolume(self, entity: Node, value: Node):
        """The volume of the journal in which the publication has been
        published. (Remark: This is currently an intermediate property that will
        be removed once journals and conference series are modelled as proper
        entities.)"""
        pass

    def hasA_publishedInJournalVolumeIssue(self, entity: Node, value: Node):
        """The issue of the journal in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInBook(self, entity: Node, value: Node):
        """The name of the book in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInBookChapter(self, entity: Node, value: Node):
        """The chapter of the book in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_pagination(self, entity: Node, value: Node):
        """The page numbers where the publication can be found."""
        pass

    def hasA_yearOfEvent(self, entity: Node, value: Node):
        """The year the conference or workshop contribution has been presented."""
        pass

    def hasA_yearOfPublication(self, entity: Node, value: Node):
        """The year the publication's issue or volume has been published."""
        pass

    def hasA_monthOfPublication(self, entity: Node, value: Node):
        """The month the publication has been published."""
        pass

    def hasA_publishedBy(self, entity: Node, value: Node):
        """The publisher of the publication. (Remark: This property currently
        just gives literal xsd:string values until publishers are modelled as
        proper entities.)

        """
        pass

    def hasA_publishersAddress(self, entity: Node, value: Node):
        """The address of the publisher. (Remark: This is currently an
        intermediate property that will be removed once publishers are modelled
        as proper entities.)

        """
        pass

    def hasA_thesisAcceptedBySchool(self, entity: Node, value: Node):
        """The school where the publication (typically a thesis) has been
        accepted. (Remark: This property currently just gives literal xsd:string
        values until institutions are modelled as proper entities.)

        """
        pass

    def hasA_publicationNote(self, entity: Node, value: Node):
        """An additional note to the publication."""
        pass

    def hasA_publishedAsPartOf(self, entity: Node, value: Node):
        """The publication has been published as a part of the other publication."""
        pass
