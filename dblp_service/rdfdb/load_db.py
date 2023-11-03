#!/usr/bin/env python3

# Write a set of sparql queries for the Apache Jena RDF database.
# Assume that there is an existing named graph in the Jena database named 'current-dblp'
# The queries should do the following:
# - Load the contents of a local rdf ttl (turtle) file named 'dblp.ttl' inta a new graph named 'updated-dblp'
# LOAD <file:///path/to/dblp.ttl> INTO GRAPH <updated-dblp>
#
#
# - Rename the database 'current-dblp' to 'prev-dblp'
# ADD GRAPH <current-dblp> TO GRAPH <prev-dblp>

# # Drop the old 'current-dblp'
# DROP GRAPH <current-dblp>

## Copy 'updated-dblp' to 'current-dblp'
# ADD GRAPH <updated-dblp> TO GRAPH <current-dblp>

# Drop the old 'updated-dblp'
# DROP GRAPH <updated-dblp>
 # - Rename the database 'updated-dblp' to 'current-dblp'
