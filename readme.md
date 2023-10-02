# DBLP query server

# Issues
- Server is throwing oom errors

# Goal
Given an author ID
> <https://dblp.org/pid/m/AndrewMcCallum>
1. Construct a list of all publications for that author
2. Return those publications as a list of DBLP records, e.g.,

```
[
    @inproceedings{DBLP:conf/conll/McCallum09,
      author       = {Andrew McCallum},
      editor       = {Suzanne Stevenson and Xavier Carreras},
      title        = {Joint Inference for Natural Language Processing},
      booktitle    = {Proceedings of the Thirteenth Conference on Computational Natural
                      Language Learning, CoNLL 2009, Boulder, Colorado, USA, June 4-5, 2009},
      pages        = {1},
      publisher    = {{ACL}},
      year         = {2009},
      url          = {https://aclanthology.org/W09-1101/},
      timestamp    = {Fri, 06 Aug 2021 00:41:15 +0200},
      biburl       = {https://dblp.org/rec/conf/conll/McCallum09.bib},
      bibsource    = {dblp computer science bibliography, https://dblp.org}
    },

    ... etc

]
```


## RDF structure

### Persons
```
<https://dblp.org/pid/304/8268>
        rdfs:label "Geunhee Kim" ;
        datacite:hasIdentifier [
                datacite:usesIdentifierScheme datacite:dblp ;
                litre:hasLiteralValue "304/8268" ;
                a datacite:PersonalIdentifier
        ] ;
        dblp:primaryCreatorName "Geunhee Kim" ;
        dblp:creatorName "Geunhee Kim" ;
        a dblp:Creator, dblp:Person .

```
