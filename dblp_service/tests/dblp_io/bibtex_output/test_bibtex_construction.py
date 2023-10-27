#!/usr/bin/env python3


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
