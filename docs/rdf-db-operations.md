# Rdf Db Operations
## Download new rdf file(s)
> download-rdf-file <file or URL> --stash
- downloads a dblp.ttl+md5 file (or takes from local)
- creates a dir named after md5, moves file there
- creates a metadata.json file with creation date

## Load new rdfs into db
> load-rdfs --stash=md5-hash / --all
load any stashed files into graphs if not already loaded
optionally load just named md5 graph?

## Diff old/new rdfs
> diff-dbs --commit-to dblp-changes
- compare graphs pairwise, from oldest to newest, recording additions for each new graph

## TODO manage local ttl files, prune old versions, keep index of available files
dates of fetch, etc.

## Example Session
> db-manage --clean --init --report
> stash --init/--update-index
> stash --report

> stash --download/--import-file --revisions-to-dl 3

> db-load --revisions = n


# The following are not db operations, refile
## List new publications
sparql query against dblp-changes graph

## List changed authors
sparql query against dblp-changes graph

## Compare new/changed pubs/authors to those in openreview
> db-diff-graphs --write-changes
## POST updates to OpenReview to fill in missing publications
