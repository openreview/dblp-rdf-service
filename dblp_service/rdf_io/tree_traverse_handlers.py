"""Tree node visitors for constructing authorship output.

Classes implement functions that match the properties contained
in authorship trees, to be called when transforming the tree
to another format, e.g., XML or bibtex.

"""

from abc import abstractmethod
import typing as t

from bigtree.node.node import Node

OutputType = t.TypeVar("OutputType")


class OutputFactory(t.Generic[OutputType]):
    """Factory to create and manipulate authorship output"""

    @abstractmethod
    def create_empty_output(self) -> OutputType:
        pass

    @abstractmethod
    def create_entity_class(self, entity: Node, entity_class: Node) -> OutputType:
        pass

    @abstractmethod
    def create_key_val_field(self, rel_type: Node, prop_val: Node, keystr: t.Optional[str]) -> OutputType:
        pass

    @abstractmethod
    def append_fields(self, field1: OutputType, field2: OutputType) -> OutputType:
        pass

    @abstractmethod
    def append_child(self, field1: OutputType, field2: OutputType) -> OutputType:
        pass

    def get_entry(self, node: Node) -> t.Optional[OutputType]:
        return node.get_attr("entry")

    def set_entry(self, node: Node, entry: OutputType) -> None:
        node.set_attrs(dict(entry=entry))

    # def get_or_create_entry(self, node: Node) -> OutputType:
    #     entry = node.get_attr("entry")
    #     if entry is None:
    #         entry = self.create_empty_output()
    #         node.set_attrs(dict(entry=entry))

    #     return entry


class AuthorshipPropertyHandlers(t.Generic[OutputType]):
    """Properties Derived from dblp/schema.rdf"""

    output_factory: OutputFactory[OutputType]

    def __init__(self, factory: OutputFactory[OutputType]):
        self.output_factory = factory



    def hasA_simple_key_val_prop(self, rel_type: Node, prop_val: Node, key: t.Optional[str] = None):
        field = self.output_factory.create_key_val_field(rel_type, prop_val, key)
        return field
        # parent_entry = self.output_factory.get_entry(entity)
        # assert parent_entry is not None
        # appended = self.output_factory.append_child(parent_entry, field)
        # self.output_factory.set_entry(entity, appended)


    def isA_Entity(self, entity: Node, prop_val: Node):
        """A general, identifiable entity in dblp."""

    def isA_Creator(self, entity: Node, prop_val: Node):
        """A creator of a publication."""

    def isA_AmbiguousCreator(self, entity: Node, prop_val: Node):
        """Not an actual creator, but an ambiguous proxy for an unknown number of unrelated actual creators. Associated publications do not have their true creators determined yet."""

    def isA_Person(self, entity: Node, prop_val: Node):
        """An actual person, who is a creator of a publication."""

    def isA_Group(self, entity: Node, prop_val: Node):
        """A creator alias used by a group or consortium of persons."""

    def isA_Signature(self, entity: Node, prop_val: Node):
        """The information that links a publication to a creator."""

    def isA_AuthorSignature(self, entity: Node, prop_val: Node):
        """The information that links a publication to an author."""

    def isA_EditorSignature(self, entity: Node, prop_val: Node):
        """The information that links a publication to an editor."""

    def isA_Publication(self, entity: Node, prop_val: Node):
        """A publication."""
        pass

    def isA_Book(self, entity: Node, prop_val: Node):
        """A book or a thesis."""
        pass

    def isA_Article(self, entity: Node, prop_val: Node):
        """A journal article."""
        pass

    def isA_Inproceedings(self, entity: Node, prop_val: Node):
        """A conference or workshop paper."""
        return self.output_factory.create_entity_class(entity, prop_val)

    def isA_Incollection(self, entity: Node, prop_val: Node):
        """A part/chapter in a book or a collection."""
        pass

    def isA_Editorship(self, entity: Node, prop_val: Node):
        """An edited publication."""
        pass

    def isA_Reference(self, entity: Node, prop_val: Node):
        """A reference work entry."""
        pass

    def isA_Data(self, entity: Node, prop_val: Node):
        """Research data or artifacts."""
        pass

    def isA_Informal(self, entity: Node, prop_val: Node):
        """An informal or other publication."""
        pass

    def isA_Withdrawn(self, entity: Node, prop_val: Node):
        """A withdrawn publication item."""
        pass

    def hasA_identifier(self, entity: Node, prop_val: Node):
        """An abstract identifier."""
        pass

    def hasA_wikidata(self, entity: Node, prop_val: Node):
        """A wikidata item."""
        pass

    def hasA_webpage(self, entity: Node, prop_val: Node):
        """The URL of a web page about this item."""
        return self.hasA_simple_key_val_prop(entity, prop_val)

    def hasA_archivedWebpage(self, entity: Node, prop_val: Node):
        """The URL of an archived web page about this item, which may no longer be available in the web."""
        pass

    def hasA_wikipedia(self, entity: Node, prop_val: Node):
        """The URL of an (English) Wikipedia article about this item."""
        pass

    def hasA_orcid(self, entity: Node, prop_val: Node):
        """An Open Researcher and Contributor ID."""
        pass

    def hasA_creatorName(self, entity: Node, prop_val: Node):
        """The full name of the creator."""
        pass

    def hasA_primaryCreatorName(self, entity: Node, prop_val: Node):
        """The primary full name of the creator."""
        pass

    def hasA_creatorNote(self, entity: Node, prop_val: Node):
        """An additional note about the creator."""
        pass

    def hasA_affiliation(self, entity: Node, prop_val: Node):
        """A (past or present) affiliation of the creator. (Remark: This
        property currently just gives literal xsd:string values until
        institutions are modelled as proper entities.
        """
        pass

    def hasA_primaryAffiliation(self, entity: Node, prop_val: Node):
        """The primary affiliation of the creator. (Remark: This property
        currently just gives literal xsd:string values until institutions are
        modelled as proper entities.)
        """
        pass

    def hasA_awardWebpage(self, entity: Node, prop_val: Node):
        """The URL of a web page about an award received by this creator."""
        pass

    def hasA_homepage(self, entity: Node, prop_val: Node):
        """The URL of an academic homepage of this creator."""
        pass

    def hasA_primaryHomepage(self, entity: Node, prop_val: Node):
        """The primary URL of an academic homepage of this creator."""
        pass

    def hasA_creatorOf(self, entity: Node, prop_val: Node):
        """The creator of the publication."""
        pass

    def hasA_authorOf(self, entity: Node, prop_val: Node):
        """The creator is the author of the publication."""
        pass

    def hasA_editorOf(self, entity: Node, prop_val: Node):
        """The creator is the editor of the publication."""
        pass

    def hasA_coCreatorWith(self, entity: Node, prop_val: Node):
        """The creator is co-creator with the other creator."""
        pass

    def hasA_coAuthorWith(self, entity: Node, prop_val: Node):
        """The creator is co-author with the other creator."""
        pass

    def hasA_coEditorWith(self, entity: Node, prop_val: Node):
        """The creator is co-editor with the other creator."""
        pass

    def hasA_homonymousCreator(self, entity: Node, prop_val: Node):
        """This creator shares a homonymous name with the other creator."""
        pass

    def hasA_possibleActualCreator(self, entity: Node, prop_val: Node):
        """This ambiguous creator may be (or may be not) just a disambiguation
        proxy for the other creator. Further actual creator candidates are
        possible.

        """
        pass

    def hasA_proxyAmbiguousCreator(self, entity: Node, prop_val: Node):
        """This creator (and any of her fellow homonymous creators) is also
        represented by the given ambiguous creator in cases where the authorship
        of a publication is undetermined.

        """
        pass

    def hasA_signatureCreator(self, entity: Node, prop_val: Node):
        """A linked creator of the publication."""
        pass

    def hasA_signatureDblpName(self, entity: Node, prop_val: Node):
        """A dblp name (including any possible trailing homonym number) that links the publication to a creator."""
        pass

    def hasA_signatureOrcid(self, entity: Node, prop_val: Node):
        """An ORCID that links the publication to a creator."""
        pass

    def hasA_signatureOrdinal(self, entity: Node, prop_val: Node):
        """The ordinal number of this signature for the publication, starting with 1."""
        pass

    def hasA_signaturePublication(self, entity: Node, prop_val: Node):
        """The publication of this signature."""
        pass

    def hasA_doi(self, entity: Node, prop_val: Node):
        """A Digital Object Identifier."""
        return self.hasA_simple_key_val_prop(entity, prop_val)

    def hasA_isbn(self, entity: Node, prop_val: Node):
        """An International Standard Book Number."""
        return self.hasA_simple_key_val_prop(entity, prop_val)

    def hasA_title(self, entity: Node, prop_val: Node):
        """The title of the publication."""
        return self.hasA_simple_key_val_prop(entity, prop_val)

    def hasA_bibtexType(self, entity: Node, prop_val: Node):
        """The bibtex type of the publication, e.g. book, inproceedings, etc."""
        pass

    def hasA_createdBy(self, entity: Node, prop_val: Node):
        """The publication is created by the creator."""
        pass

    def hasA_authoredBy(self, entity: Node, prop_val: Node):
        """The publication is authored by the creator."""
        pass

    def hasA_editedBy(self, entity: Node, prop_val: Node):
        """The publication is edited by the creator."""
        pass

    def hasA_numberOfCreators(self, entity: Node, prop_val: Node):
        """The number of creators who created this publication."""
        pass

    def hasA_hasSignature(self, entity: Node, prop_val: Node):
        """A signature that links this publication to an creator."""
        pass

    def hasA_documentPage(self, entity: Node, prop_val: Node):
        """The URL of the electronic edition of the publication."""
        pass

    def hasA_primarydocumentPage(self, entity: Node, prop_val: Node):
        """The primary URL of the electronic edition of the publication."""
        pass

    def hasA_listedOnTocPage(self, entity: Node, prop_val: Node):
        """The url of the dblp table of contents page listing this publication."""
        pass

    def hasA_publishedIn(self, entity: Node, prop_val: Node):
        """The name of the series, the journal, or the book in which the
        publication has been published. (Remark: This property currently just
        gives literal xsd:string values until journals and conference series are
        modelled as proper entities.)

        """
        pass

    def hasA_publishedInSeries(self, entity: Node, prop_val: Node):
        """The name of the series in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInSeriesVolume(self, entity: Node, prop_val: Node):
        """The volume of the series in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)"""
        pass

    def hasA_publishedInJournal(self, entity: Node, prop_val: Node):
        """The name of the journal in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInJournalVolume(self, entity: Node, prop_val: Node):
        """The volume of the journal in which the publication has been
        published. (Remark: This is currently an intermediate property that will
        be removed once journals and conference series are modelled as proper
        entities.)"""
        pass

    def hasA_publishedInJournalVolumeIssue(self, entity: Node, prop_val: Node):
        """The issue of the journal in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInBook(self, entity: Node, prop_val: Node):
        """The name of the book in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_publishedInBookChapter(self, entity: Node, prop_val: Node):
        """The chapter of the book in which the publication has been published.
        (Remark: This is currently an intermediate property that will be removed
        once journals and conference series are modelled as proper entities.)

        """
        pass

    def hasA_pagination(self, entity: Node, prop_val: Node):
        """The page numbers where the publication can be found."""
        pass

    def hasA_yearOfEvent(self, entity: Node, prop_val: Node):
        """The year the conference or workshop contribution has been presented."""
        return self.hasA_simple_key_val_prop(entity, prop_val, "year")

    def hasA_yearOfPublication(self, entity: Node, prop_val: Node):
        """The year the publication's issue or volume has been published."""
        return self.hasA_simple_key_val_prop(entity, prop_val, "year")

    def hasA_monthOfPublication(self, entity: Node, prop_val: Node):
        """The month the publication has been published."""
        pass

    def hasA_publishedBy(self, entity: Node, prop_val: Node):
        """The publisher of the publication. (Remark: This property currently
        just gives literal xsd:string values until publishers are modelled as
        proper entities.)

        """
        pass

    def hasA_publishersAddress(self, entity: Node, prop_val: Node):
        """The address of the publisher. (Remark: This is currently an
        intermediate property that will be removed once publishers are modelled
        as proper entities.)

        """
        pass

    def hasA_thesisAcceptedBySchool(self, entity: Node, prop_val: Node):
        """The school where the publication (typically a thesis) has been
        accepted. (Remark: This property currently just gives literal xsd:string
        values until institutions are modelled as proper entities.)

        """
        pass

    def hasA_publicationNote(self, entity: Node, prop_val: Node):
        """An additional note to the publication."""
        pass

    def hasA_publishedAsPartOf(self, entity: Node, prop_val: Node):
        """The publication has been published as a part of the other publication."""
        pass


# class AuthorshipClassHandlers(t.Generic[OutputType]):
#     """Classes Derived from dblp/schema.rdf"""

#     output_factory: OutputFactory[OutputType]

#     def isA_Entity(self, entity: Node):
#         """A general, identifiable entity in dblp."""

#     def isA_Creator(self, entity: Node):
#         """A creator of a publication."""

#     def isA_AmbiguousCreator(self, entity: Node):
#         """Not an actual creator, but an ambiguous proxy for an unknown number of unrelated actual creators. Associated publications do not have their true creators determined yet."""

#     def isA_Person(self, entity: Node):
#         """An actual person, who is a creator of a publication."""

#     def isA_Group(self, entity: Node):
#         """A creator alias used by a group or consortium of persons."""

#     def isA_Signature(self, entity: Node):
#         """The information that links a publication to a creator."""

#     def isA_AuthorSignature(self, entity: Node):
#         """The information that links a publication to an author."""

#     def isA_EditorSignature(self, entity: Node):
#         """The information that links a publication to an editor."""

#     def isA_Publication(self, entity: Node):
#         """A publication."""
#         pass

#     def isA_Book(self, entity: Node):
#         """A book or a thesis."""
#         pass

#     def isA_Article(self, entity: Node):
#         """A journal article."""
#         pass

#     def isA_Inproceedings(self, entity: Node):
#         """A conference or workshop paper."""
#         print("Calling super inpro")

#     def isA_Incollection(self, entity: Node):
#         """A part/chapter in a book or a collection."""
#         pass

#     def isA_Editorship(self, entity: Node):
#         """An edited publication."""
#         pass

#     def isA_Reference(self, entity: Node):
#         """A reference work entry."""
#         pass

#     def isA_Data(self, entity: Node):
#         """Research data or artifacts."""
#         pass

#     def isA_Informal(self, entity: Node):
#         """An informal or other publication."""
#         pass

#     def isA_Withdrawn(self, entity: Node):
#         """A withdrawn publication item."""
#         pass
