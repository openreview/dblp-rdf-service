from textwrap import dedent

AUTHOR_1_TREE = dedent("""
    https://dblp.org/rec/conf/acl/DruckGG11
    ├── https://dblp.org/rdf/schema#hasSignature
    │   └── b8
    │       ├── http://www.w3.org/1999/02/22-rdf-syntax-ns#type
    │       │   └── https://dblp.org/rdf/schema#AuthorSignature
    │       ├── https://dblp.org/rdf/schema#signaturePublication
    │       │   └── https://dblp.org/rec/conf/acl/DruckGG11
    │       ├── https://dblp.org/rdf/schema#signatureDblpName
    │       │   └── Gregory Druck
    │       ├── https://dblp.org/rdf/schema#signatureCreator
    │       │   └── https://dblp.org/pid/66/4867
    │       ├── https://dblp.org/rdf/schema#signatureOrdinal
    │       │   └── 1
    │       └── isA
    │           └── https://dblp.org/rdf/schema#AuthorSignature
    └── isA
        ├── https://dblp.org/rdf/schema#Inproceedings
        └── https://dblp.org/rdf/schema#Publication
""")

AUTHOR_1_TUPLES = dedent("""
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signaturePublication', bobj='https://dblp.org/rec/conf/acl/DruckGG11')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signatureDblpName', bobj='Gregory Druck')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signatureCreator', bobj='https://dblp.org/pid/66/4867')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='https://dblp.org/rdf/schema#signatureOrdinal', bobj='1')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='isA', obj='https://dblp.org/rdf/schema#Inproceedings', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='isA', obj='https://dblp.org/rdf/schema#Publication', bpred=None, bobj=None)
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b8', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
""")

AUTHOR_2_TUPLES = dedent("""
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='isA', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='http://www.w3.org/1999/02/22-rdf-syntax-ns#type', bobj='https://dblp.org/rdf/schema#AuthorSignature')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signaturePublication', bobj='https://dblp.org/rec/conf/acl/DruckGG11')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signatureDblpName', bobj='Kuzman Ganchev')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signatureCreator', bobj='https://dblp.org/pid/43/5339')
    ('https://dblp.org/rec/conf/acl/DruckGG11', pred='https://dblp.org/rdf/schema#hasSignature', obj='b9', bpred='https://dblp.org/rdf/schema#signatureOrdinal', bobj='2')
""")
