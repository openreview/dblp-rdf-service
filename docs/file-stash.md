# File Stash

The file stash component is responsible for maintaining the downloaded DBLP RDF files.

It's operations include:
- fetch the full catalog of database exports from dblp.org, which includes a list of date stamped releases in addition to the most current export.

The MD5 hashes of the base version that is currently in use, as well as the head version for the purpose of computing updates and diffs to develop.

## Operation walkthrough
> stash update
> stash report
> stash set-base
> stash set-base 8156
> stash download
> stash set-head 929
> stash set-head
> stash download
> stash purge

# DBLP File Fetcher
