# Author Alignment

## Publication alignment cases

### Publication appears in Both OpenReview and dblp.org
   - Optional output feature for publications available on both platforms.

### Publications appear only in OpenReview
- Potential indication of outdated dblp.com catalog.
    - Identify the OpenReview note's publication/creation date.
    - Compare with the creation date of the most recent dblp.org database.
    - If the note is newer, let the user know that  a dblp database update might fix it.
    - Otherwise warn the user


### Publications appear only in dblp.org
   - Expand the table with additional records.
   - Strategies:
     - Implement a title search to find or create matching records.
     - Consider the option for a future DOI or DBLP PID search (currently inefficient in Open Review).
     - Develop a list of candidate papers for linking to the author under scrutiny.
     - Output corrective measures (dry run post data).
     - For papers not found:
       - Post new paper data and immediately link the author under scrutiny.

## Other Considerations
### Duplicate publications
#### OpenReview Note duplicates
#### dlbp.org publication duplicates
### Accuracy of matching procedure betweeen OpenReview and dblp papers
  Currently relies on exact match over title words, which is brittle and error prone.

  Consider efficient openreview lookup by, e.g., DOI, dblp id ('/m/conl09/MSmith34'), arXiv id.
