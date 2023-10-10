# Dev tasks/notes

## Overview
For every person/author profile in  OpenReview, supplement their set of authored
papers by identifying them in DBLP and uploading any dblp records (as new notes)
that are not  already recorded present. As dblp.org updates  their database with
new papers, add any new entries into OpenReview



## Requirements


### Components
### Local copy of dblp database
- create
- Update dblp data to latest version




### Deployment


## Tasks


- scripts to download most recent dblp.ttl data and load into Jena
- scripts to setup and run Jena server


## Issues

- Server is throwing OOM errors

### Extraction Service process

- Get all notes authored by author=${profileId}
   - getProfile('~ACSaunders') or:/../profiles
   - getAllPapersByGroupId('~ACSaunders') or:/../notes
     - returns notes as list of strings = normalized titles

- Profiles *should* have a field `profile.content.dblp`
  equal to something like:  'https://dblp.org://../m/Author.xml'
  https://dblp.org/pers/m/McCallum:Andrew.html

- ?? Only upload new papers if there are no papers of any kind for that author


This line makes no sense to me:
    >>  if (dblpUrlCandidateSplit[1].startsWith('pid') || dblpUrlCandidateSplit[1].startsWith('~ley')) {

- Fetch content of 'dblp.org://../m/Author.xml'
- From fetched content, extract the dblp persistent id, e.g., y/AriShapiro
  - Is it always different from the content.dblp field?
  - The  dblp url extracted from dblp.org://*.xml will be used to update/overwrite the content.dblp field



- Construct a record of the form (which will form the POST of an initial note)
```
      return {
        note: {
          content: {
            dblp: publicationNode.toString()
          },
          invitation: 'dblp.org/-/record',
          readers: ['everyone'],
          writers: ['dblp.org'],
          signatures: ['dblp.org']
        },
        title: publicationNode.getElementsByTagName('title')[0].textContent,
        authorIndex: Array.from(publicationNode.getElementsByTagName('author')).map(p => p.getAttribute('pid')).indexOf(authorPidInXML)
      };
```

- If note exist in OpenReview, POST update
```

  let updateNoteObject = {
    id: referenceId,
    referent: paperId,
    invitation: 'dblp.org/-/author_coreference',
    signatures: ['dblp.org'],
    readers: ['everyone'],
    writers: [],
    content: {
      authorids: authorIds
    }
```
- Else if note !exist in OpenReview, POST initial note, then POST update



Hi Melisa,
I just want to double check on exactly what the required inputs/outputs are for the DBLP system, in terms of both the required fields and the preferred output format. My current understanding is this:
Given an input ID of the form:
    https://dblp.org/pid/m/AndrewMcCallum
1. Find the list of all publications for that author
2. Return those publications as a list of records, where each record contains some basic information (e.g., title, authors)
3. The author list for  each publication only needs to be the URL, e.g, https://dblp.org/pid/m/SomeName.
Here is what a sample returned record might look like, with a few question embedded, prefixed with ??:
[
?? Should the format be BibTex? Or just key/value pairs in JSON or XML (or other format)?
@inproceedings{DBLP:conf/eacl/RongaliSKAHM23,

 authorids       = {https://dblp.org/pid/Rongali, etc...},
?? Do we need the names of the co-authors, or just IDs as above?
  author       = {Subendhu Rongali and Mukund Sridhar and Andrew McCallum},
?? Do we need any of the other available fields, in particular title/booktitle?:
  editor       = {Andreas Vlachos and Isabelle Augenstein},
  title        = {Low-Resource Compositional Semantic Parsing with Concept Pretraining},
  booktitle    = {Proceedings of the 17th Conference of the European Chapter of the
                  Association for Computational Linguistics, {EACL} 2023, Dubrovnik,
                  Croatia, May 2-6, 2023},
  pages        = {1402--1411},
  publisher    = {Association for Computational Linguistics},
  year         = {2023},
  url          = {https://aclanthology.org/2023.eacl-main.103},
  timestamp    = {Thu, 11 May 2023 17:08:21 +0200},
  biburl       = {https://dblp.org/rec/conf/eacl/RongaliSKAHM23.bib},
