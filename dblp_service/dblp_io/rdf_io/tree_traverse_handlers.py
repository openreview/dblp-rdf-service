"""Tree node visitors for constructing authorship output.

Classes implement functions that match the properties contained
in authorship trees, to be called when transforming the tree
to another format, e.g., XML or bibtex.

"""

import typing as t
from bigtree.node.node import Node
from dblp_service.dblp_io.rdf_io.dblp_repr import KeyValProp, NameSpec, Publication, ResourceIdentifier
from dblp_service.dblp_io.rdf_io.trees import simplify_urlname

from dblp_service.lib.predef.utils import to_int


class AuthorshipPropertyHandlers:
    """Properties Derived from dblp/schema.rdf"""

    def hasA_simple_key_val_prop(self, rel_type: Node, prop_val: Node, keystr: t.Optional[str] = None):
        name = keystr if keystr else simplify_urlname(rel_type.node_name)
        value = prop_val.node_name
        return KeyValProp(name, value)

    # def isA_Entity(self, entity: Node, prop_val: Node):
    #     """A general, identifiable entity in dblp."""

    # def isA_Creator(self, entity: Node, prop_val: Node):
    #     """A creator of a publication."""

    # def isA_AmbiguousCreator(self, entity: Node, prop_val: Node):
    #     """Not an actual creator, but an ambiguous proxy for an unknown number of unrelated actual creators. Associated publications do not have their true creators determined yet."""

    # def isA_Person(self, entity: Node, prop_val: Node):
    #     """An actual person, who is a creator of a publication."""

    # def isA_Group(self, entity: Node, prop_val: Node):
    #     """A creator alias used by a group or consortium of persons."""

    def isA_Publication(self, entity: Node, prop_val: Node):
        """A publication."""
        key = simplify_urlname(prop_val.node_name)
        return Publication(pub_type=key)

    def isA_Book(self, entity: Node, prop_val: Node):
        """A book or a thesis."""
        key = simplify_urlname(prop_val.node_name)
        return Publication(pub_type=key)

    def isA_Article(self, entity: Node, prop_val: Node):
        """A journal article."""
        key = simplify_urlname(prop_val.node_name)
        return Publication(pub_type=key)

    def isA_Inproceedings(self, entity: Node, prop_val: Node):
        """A conference or workshop paper."""
        key = simplify_urlname(prop_val.node_name)
        return Publication(pub_type=key)

    def isA_Incollection(self, entity: Node, prop_val: Node):
        """A part/chapter in a book or a collection."""
        key = simplify_urlname(prop_val.node_name)
        return Publication(pub_type=key)

    def hasA_doi(self, rel: Node, prop_val: Node):
        """A Digital Object Identifier."""
        return self.hasA_simple_key_val_prop(rel, prop_val)

    def hasA_isbn(self, rel: Node, prop_val: Node):
        """An International Standard Book Number."""
        return self.hasA_simple_key_val_prop(rel, prop_val)

    def hasA_title(self, rel: Node, prop_val: Node):
        """The title of the publication."""
        return self.hasA_simple_key_val_prop(rel, prop_val)

    def hasA_yearOfEvent(self, rel: Node, prop_val: Node):
        """The year the conference or workshop contribution has been presented."""
        return self.hasA_simple_key_val_prop(rel, prop_val, "year")

    def hasA_yearOfPublication(self, rel: Node, prop_val: Node):
        """The year the publication's issue or volume has been published."""
        return self.hasA_simple_key_val_prop(rel, prop_val, "year")

    def hasA_webpage(self, rel: Node, prop_val: Node):
        """The URL of a web page about this item."""
        return self.hasA_simple_key_val_prop(rel, prop_val)

    ####
    ## Signature properties
    def isA_Signature(self, entity: Node, prop_val: Node):
        """The information that links a publication to a creator."""
        # add empty signature, overwritable

    def isA_AuthorSignature(self, entity: Node, prop_val: Node):
        """The information that links a publication to an author.

        Expected input tree shape:

                        https://dblp.org/rdf/schema#hasSignature
           entity   ->  ├── b2
                        │   ├── http://www.w3.org/1999/02/22-rdf-syntax-ns#type
                        │   │   └── https://dblp.org/rdf/schema#AuthorSignature
                        │   ├── https://dblp.org/rdf/schema#signaturePublication
                        │   │   └── https://dblp.org/rec/conf/cikm/DruckM11
                        │   ├── https://dblp.org/rdf/schema#signatureDblpName
                        │   │   └── Gregory Druck
                        │   ├── https://dblp.org/rdf/schema#signatureCreator
                        │   │   └── https://dblp.org/pid/66/4867
                        │   ├── https://dblp.org/rdf/schema#signatureOrdinal
                        │   │   └── 1
           isA      ->  │   └── isA
           prop_val ->  │       └── https://dblp.org/rdf/schema#AuthorSignature

        Output:
          Set entity b2.entry = NameSpec("author")
        """
        return NameSpec(name_type="author")

    def isA_EditorSignature(self, entity: Node, prop_val: Node):
        """The information that links a publication to an editor."""
        return NameSpec(name_type="editor")

    def hasA_signatureDblpName(self, rel: Node, prop_val: Node):
        """A dblp name (including any possible trailing homonym number) that links the publication to a creator."""
        return NameSpec(fullname=prop_val.node_name)

    def hasA_signatureOrdinal(self, rel: Node, prop_val: Node):
        """The ordinal number of this signature for the publication, starting with 1."""
        ordinal = to_int(prop_val.node_name)
        assert isinstance(ordinal, int)
        return NameSpec(ordinal=ordinal)

    def hasA_hasSignature(self, rel: Node, prop_val: Node):
        """A signature that links this publication to an creator.

        entity -> https://dblp.org/rec/conf/cikm/DruckM11
        rel    -> ├── https://dblp.org/rdf/schema#hasSignature
        prop   -> │   ├── b2
                  │   │   ├── https://dblp.org/rdf/schema#signatureDblpName

        """
        return prop_val.get_attr("entry")

    # def hasA_signatureCreator(self, rel: Node, prop_val: Node):
    #     """A linked creator of the publication."""
    # def hasA_signatureOrcid(self, rel: Node, prop_val: Node):
    #     """An ORCID that links the publication to a creator."""
    # def hasA_signaturePublication(self, rel: Node, prop_val: Node):
    #     """The publication of this signature."""

    ## End Signature properties

    ####
    ## Resource Identifiers
    def isA_ResourceIdentifier(self, entity: Node, prop_val: Node):
        """Identifier, e.g., doi, dblp pid

        blank0
        ├── http://www.w3.org/1999/02/22-rdf-syntax-ns#type
        │   └── http://purl.org/spar/datacite/ResourceIdentifier
        ├── http://purl.org/spar/literal/hasLiteralValue
        │   └── conf/cikm/DruckM11
        ├── http://purl.org/spar/datacite/usesIdentifierScheme
        │   └── http://purl.org/spar/datacite/dblp-record
        └── isA
           └── http://purl.org/spar/datacite/ResourceIdentifier

        """
        return ResourceIdentifier()

    def hasA_type(self, rel: Node, prop_val: Node):
        """"""

    def hasA_hasLiteralValue(self, rel: Node, prop_val: Node):
        """"""
        return ResourceIdentifier(value=prop_val.node_name)

    def hasA_usesIdentifierScheme(self, rel: Node, prop_val: Node):
        return ResourceIdentifier(id_scheme=prop_val.node_name)
        """"""

    # def hasA_identifier(self, rel: Node, prop_val: Node):
    #     """An abstract identifier."""
    #     pass

    # def isA_Editorship(self, entity: Node, prop_val: Node):
    #     """An edited publication."""
    #     pass

    # def isA_Reference(self, entity: Node, prop_val: Node):
    #     """A reference work entry."""
    #     pass

    # def isA_Data(self, entity: Node, prop_val: Node):
    #     """Research data or artifacts."""
    #     pass

    # def isA_Informal(self, entity: Node, prop_val: Node):
    #     """An informal or other publication."""
    #     pass

    # def isA_Withdrawn(self, entity: Node, prop_val: Node):
    #     """A withdrawn publication item."""
    #     pass

    # def hasA_wikidata(self, rel: Node, prop_val: Node):
    #     """A wikidata item."""
    #     pass

    # def hasA_archivedWebpage(self, rel: Node, prop_val: Node):
    #     """The URL of an archived web page about this item, which may no longer be available in the web."""
    #     pass

    # def hasA_wikipedia(self, rel: Node, prop_val: Node):
    #     """The URL of an (English) Wikipedia article about this item."""
    #     pass

    # def hasA_orcid(self, rel: Node, prop_val: Node):
    #     """An Open Researcher and Contributor ID."""
    #     pass

    # def hasA_creatorName(self, rel: Node, prop_val: Node):
    #     """The full name of the creator."""
    #     pass

    # def hasA_primaryCreatorName(self, rel: Node, prop_val: Node):
    #     """The primary full name of the creator."""
    #     pass

    # def hasA_creatorNote(self, rel: Node, prop_val: Node):
    #     """An additional note about the creator."""
    #     pass

    # def hasA_affiliation(self, rel: Node, prop_val: Node):
    #     """A (past or present) affiliation of the creator. (Remark: This
    #     property currently just gives literal xsd:string values until
    #     institutions are modelled as proper entities.
    #     """
    #     pass

    # def hasA_primaryAffiliation(self, rel: Node, prop_val: Node):
    #     """The primary affiliation of the creator. (Remark: This property
    #     currently just gives literal xsd:string values until institutions are
    #     modelled as proper entities.)
    #     """
    #     pass

    # def hasA_awardWebpage(self, rel: Node, prop_val: Node):
    #     """The URL of a web page about an award received by this creator."""
    #     pass

    # def hasA_homepage(self, rel: Node, prop_val: Node):
    #     """The URL of an academic homepage of this creator."""
    #     pass

    # def hasA_primaryHomepage(self, rel: Node, prop_val: Node):
    #     """The primary URL of an academic homepage of this creator."""
    #     pass

    # def hasA_creatorOf(self, rel: Node, prop_val: Node):
    #     """The creator of the publication."""
    #     pass

    # def hasA_authorOf(self, rel: Node, prop_val: Node):
    #     """The creator is the author of the publication."""
    #     pass

    # def hasA_editorOf(self, rel: Node, prop_val: Node):
    #     """The creator is the editor of the publication."""
    #     pass

    # def hasA_coCreatorWith(self, rel: Node, prop_val: Node):
    #     """The creator is co-creator with the other creator."""
    #     pass

    # def hasA_coAuthorWith(self, rel: Node, prop_val: Node):
    #     """The creator is co-author with the other creator."""
    #     pass

    # def hasA_coEditorWith(self, rel: Node, prop_val: Node):
    #     """The creator is co-editor with the other creator."""
    #     pass

    # def hasA_homonymousCreator(self, rel: Node, prop_val: Node):
    #     """This creator shares a homonymous name with the other creator."""
    #     pass

    # def hasA_possibleActualCreator(self, rel: Node, prop_val: Node):
    #     """This ambiguous creator may be (or may be not) just a disambiguation
    #     proxy for the other creator. Further actual creator candidates are
    #     possible.

    #     """
    #     pass

    # def hasA_proxyAmbiguousCreator(self, rel: Node, prop_val: Node):
    #     """This creator (and any of her fellow homonymous creators) is also
    #     represented by the given ambiguous creator in cases where the authorship
    #     of a publication is undetermined.

    #     """
    #     pass

    # def hasA_bibtexType(self, rel: Node, prop_val: Node):
    #     """The bibtex type of the publication, e.g. book, inproceedings, etc."""
    #     pass

    # def hasA_createdBy(self, rel: Node, prop_val: Node):
    #     """The publication is created by the creator."""
    #     pass

    # def hasA_authoredBy(self, rel: Node, prop_val: Node):
    #     """The publication is authored by the creator."""
    #     pass

    # def hasA_editedBy(self, rel: Node, prop_val: Node):
    #     """The publication is edited by the creator."""
    #     pass

    # def hasA_numberOfCreators(self, rel: Node, prop_val: Node):
    #     """The number of creators who created this publication."""
    #     pass

    # def hasA_documentPage(self, rel: Node, prop_val: Node):
    #     """The URL of the electronic edition of the publication."""
    #     pass

    # def hasA_primarydocumentPage(self, rel: Node, prop_val: Node):
    #     """The primary URL of the electronic edition of the publication."""
    #     pass

    # def hasA_listedOnTocPage(self, rel: Node, prop_val: Node):
    #     """The url of the dblp table of contents page listing this publication."""
    #     pass

    # def hasA_publishedIn(self, rel: Node, prop_val: Node):
    #     """The name of the series, the journal, or the book in which the
    #     publication has been published. (Remark: This property currently just
    #     gives literal xsd:string values until journals and conference series are
    #     modelled as proper entities.)

    #     """
    #     pass

    # def hasA_publishedInSeries(self, rel: Node, prop_val: Node):
    #     """The name of the series in which the publication has been published.
    #     (Remark: This is currently an intermediate property that will be removed
    #     once journals and conference series are modelled as proper entities.)

    #     """
    #     pass

    # def hasA_publishedInSeriesVolume(self, rel: Node, prop_val: Node):
    #     """The volume of the series in which the publication has been published.
    #     (Remark: This is currently an intermediate property that will be removed
    #     once journals and conference series are modelled as proper entities.)"""
    #     pass

    # def hasA_publishedInJournal(self, rel: Node, prop_val: Node):
    #     """The name of the journal in which the publication has been published.
    #     (Remark: This is currently an intermediate property that will be removed
    #     once journals and conference series are modelled as proper entities.)

    #     """
    #     pass

    # def hasA_publishedInJournalVolume(self, rel: Node, prop_val: Node):
    #     """The volume of the journal in which the publication has been
    #     published. (Remark: This is currently an intermediate property that will
    #     be removed once journals and conference series are modelled as proper
    #     entities.)"""
    #     pass

    # def hasA_publishedInJournalVolumeIssue(self, rel: Node, prop_val: Node):
    #     """The issue of the journal in which the publication has been published.
    #     (Remark: This is currently an intermediate property that will be removed
    #     once journals and conference series are modelled as proper entities.)

    #     """
    #     pass

    # def hasA_publishedInBook(self, rel: Node, prop_val: Node):
    #     """The name of the book in which the publication has been published.
    #     (Remark: This is currently an intermediate property that will be removed
    #     once journals and conference series are modelled as proper entities.)

    #     """
    #     pass

    # def hasA_publishedInBookChapter(self, rel: Node, prop_val: Node):
    #     """The chapter of the book in which the publication has been published.
    #     (Remark: This is currently an intermediate property that will be removed
    #     once journals and conference series are modelled as proper entities.)

    #     """
    #     pass

    # def hasA_pagination(self, rel: Node, prop_val: Node):
    #     """The page numbers where the publication can be found."""
    #     pass

    # def hasA_monthOfPublication(self, rel: Node, prop_val: Node):
    #     """The month the publication has been published."""
    #     pass

    # def hasA_publishedBy(self, rel: Node, prop_val: Node):
    #     """The publisher of the publication. (Remark: This property currently
    #     just gives literal xsd:string values until publishers are modelled as
    #     proper entities.)

    #     """
    #     pass

    # def hasA_publishersAddress(self, rel: Node, prop_val: Node):
    #     """The address of the publisher. (Remark: This is currently an
    #     intermediate property that will be removed once publishers are modelled
    #     as proper entities.)

    #     """
    #     pass

    # def hasA_thesisAcceptedBySchool(self, rel: Node, prop_val: Node):
    #     """The school where the publication (typically a thesis) has been
    #     accepted. (Remark: This property currently just gives literal xsd:string
    #     values until institutions are modelled as proper entities.)

    #     """
    #     pass

    # def hasA_publicationNote(self, rel: Node, prop_val: Node):
    #     """An additional note to the publication."""
    #     pass

    # def hasA_publishedAsPartOf(self, rel: Node, prop_val: Node):
    #     """The publication has been published as a part of the other publication."""
    #     pass
