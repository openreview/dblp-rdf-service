""" Maintain RDF DB files on local drive .
"""


class RDFFileManager:
    # root dir where files are managed
    root_path: str

    def add_ttl_file(self):
        """Store ttl/mdf files in timestamped directories"""

    def list_ttl_files(self):
        """Return the list of *.ttl files on disk"""

    def prune_ttl_files(self):
        """Delete all but the most recent *n* ttl/md5 files"""

    def update_rdf_metadata(self):
        """ """
