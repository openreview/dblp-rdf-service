# Tasks
## NOW Diff 2 dblp rdf dumps
    - Use grep/count/uniq to find new entries
    - Use jena/sparql
      - load 2 named graphs, then use select/filter
    - Use `rdfdiff` command, but it runs out of memory


- Load up trival rdf datasets, into 2 named graphs
- launch fuseki to view them

Query to diff 2 graphs
select ?s where {
  graph <https://openreview.org/graph#l3db> { ?s a Publication }
  FILTER(! isblank(?s))
  FILTER NOT EXISTS { graph <https://openreview.org/graph#l2db> { ?s a Publication } }
}

- Procedure:
  - Download latest dblp.ttl (cli)
  - extract and load into jena (cli)
  - rotate rdf dbs (cli)
    - delete prev
    - default -> prev
    - newest -> default
  - run diff query to determine all new pubs/authors
    - record locally to keep track of update progress and report changes
  - update openreview with each new change



## Verify that Bibtex output is complete and valid via test cases
    - maybe integrate into running system to validate on the fly, report err/warnings

## Current goals
### Goal for periodic run:
    Diff updated dblp.org rdfs
    - foreach new paper, collect authors
    - foreach uniq author
      if author in openreview, add new/missing paper(s)

### Given a pid, show differences between author#pid in openreview and dblp
    - CLI
    - Option to commit changes or just show what would be changed

### Given a paperid, fetch bibtex from dblp.org, compare to locally built version
