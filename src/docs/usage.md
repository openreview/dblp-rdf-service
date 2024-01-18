# End To End Operation

3. **Documentation and CLI Application**:
    - Document the steps required for performing all valid operations.
    - Possibly integrate this documentation within the CLI application.
    - Personally test and estimate the time required for each operation.
    - Note: Operations are expected to be performed monthly or bimonthly due to significant waiting times.

## Process to iterate over all new entries in the DBLP RDF database.
    - Identify affected authors and papers.
    - Execute the complete alignment process for each author, or a necessary subsection of it.
    - This is a critical operation and must be fully functional.

5. **Tracking and Asynchronous Processing**:
    - Develop a method to iteratively track processed and pending items.
    - Anticipate handling hundreds to thousands of authors.
    - Ensure the system is asynchronous, restartable, and idempotent/reentrant.
    - The system should maintain records of monthly updates for reporting purposes.


7. **Updates and Improvements in System Components**:
    - Ensure the BibTeX versions of new papers are correct and align with those in the Open Review system.
    - Provide a clear method for modifying or augmenting BibTeX entries if needed.

**Additional Notes**:
- There are two different code paths for similar operations.
  - Front-end initial path
  - Backend update path
