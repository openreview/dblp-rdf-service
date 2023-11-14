# Dblp Rdf Notes

```
number of top level <http//.. items
➜  rg -c '^<h' dblp.ttl
10,216,087


➜  rg -c 'dblp:Publication' dblp.ttl
6,874,984


count 'a dblp:Publication ...'
➜  wc --lines pub.types.txt
10,215,118 pub.types.txt

➜  wc --lines alt-types.txt
10,216,085 alt-types.txt


➜  sort pub.types.txt| uniq -c
  13265         a dblp:Creator, dblp:AmbiguousCreator .
    343         a dblp:Creator, dblp:Group .
3326575         a dblp:Creator, dblp:Person .
2693264         a dblp:Publication, dblp:Article .
 135189         a dblp:Publication, dblp:Book .
   4623         a dblp:Publication, dblp:Data .
  58509         a dblp:Publication, dblp:Editorship .
  42726         a dblp:Publication, dblp:Incollection .
 583371         a dblp:Publication, dblp:Informal .
3321842         a dblp:Publication, dblp:Inproceedings .
  27366         a dblp:Publication, dblp:Reference .
   8045         a dblp:Publication, dblp:Withdrawn .







All isA types
   1   │  684436         a datacite:Identifier
   2   │ 3567225         a datacite:PersonalIdentifier
   3   │ 13063467        a datacite:ResourceIdentifier
   4   │   84359         a datacite:ResourceIdentifier ;
   5   │ 22069392        a dblp:AuthorSignature
   6   │   13269     a dblp:Creator, dblp:AmbiguousCreator .
   7   │     343     a dblp:Creator, dblp:Group .
   8   │ 3327538     a dblp:Creator, dblp:Person .
   9   │  141796         a dblp:EditorSignature
  10   │ 2693264     a dblp:Publication, dblp:Article .
  11   │  135189     a dblp:Publication, dblp:Book .
  12   │    4623     a dblp:Publication, dblp:Data .
  13   │   58509     a dblp:Publication, dblp:Editorship .
  14   │   42726     a dblp:Publication, dblp:Incollection .
  15   │  583371     a dblp:Publication, dblp:Informal .
  16   │ 3321842     a dblp:Publication, dblp:Inproceedings .
  17   │   27366     a dblp:Publication, dblp:Reference .
  18   │    8045     a dblp:Publication, dblp:Withdrawn .
  19   │      10     a owl:DeprecatedProperty ;
  20   │       1     a owl:Ontology ;
  21   │      52     a rdf:Property ;
  22   │       4     a rdf:Property, owl:SymmetricProperty ;
  23   │       1     a rdf:Property, owl:TransitiveProperty ;
  24   │      18     a rdfs:Class ;

```
