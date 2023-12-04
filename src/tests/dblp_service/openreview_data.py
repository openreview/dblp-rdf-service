import json
from dblp_service.open_exchange.note_schemas import Note, NoteContent, Notes, load_notes
import dataclasses as dc


note_samples = {
    'DruckM10': {
        'content': {
            '_bibtex': '@inproceedings{DBLP:conf/icml/DruckM10,\n'
            '  author={Gregory Druck and Andrew McCallum},\n'
            '  title={High-Performance Semi-Supervised Learning '
            'using Discriminatively Constrained Generative Models},\n'
            '  year={2010},\n'
            '  cdate={1262304000000},\n'
            '  pages={319-326},\n'
            '  '
            'url={https://icml.cc/Conferences/2010/papers/643.pdf},\n'
            '  booktitle={ICML},\n'
            '  crossref={conf/icml/2010}\n'
            '}\n',
            'abstract': 'We develop a semi-supervised learning method that ' 'results on CoNLL03 NER.',
            'authorids': ['~Gregory_Druck1', '~Andrew_McCallum1'],
            'authors': ['Gregory Druck', 'Andrew McCallum'],
            'errors': None,
            'html': None,
            'paperhash': 'druck|highperformance_semisupervised_learning_using_discriminatively_constrained_generative_models',
            'title': 'High-Performance Semi-Supervised Learning using '
            'Discriminatively Constrained Generative Models',
            'venue': 'ICML 2010',
            'venueid': 'dblp.org/conf/ICML/2010',
        },
        'forum': 'BJ4cr2-O-B',
        'id': 'BJ4cr2-O-B',
        'invitation': 'dblp.org/-/record',
        'number': 55038,
        'signatures': ['dblp.org'],
    },
    'DruckGG11': {
        'content': {
            '_bibtex': '@inproceedings{DBLP:conf/acl/DruckGG11,\n'
            '  author={Gregory Druck and Kuzman Ganchev and João '
            'Graça},\n'
            '  title={Rich Prior Knowledge in Learning for Natural '
            'Language Processing},\n'
            '  year={2011},\n'
            '  cdate={1293840000000},\n'
            '  pages={5},\n'
            '  url={http://www.aclweb.org/anthology/P11-5005},\n'
            '  booktitle={ACL (Tutorial Abstracts)},\n'
            '  crossref={conf/acl/2011t}\n'
            '}\n',
            'abstract': 'Gregory Druck, Kuzman Ganchev, João Graça. '
            'Proceedings of the 49th Annual Meeting of the '
            'Association for Computational Linguistics: Tutorial '
            'Abstracts. 2011.',
            'authorids': ['~Gregory_Druck1', '~Kuzman_Ganchev1', '~João_Graça1'],
            'authors': ['Gregory Druck', 'Kuzman Ganchev', 'João Graça'],
            'errors': None,
            'html': 'http://www.aclweb.org/anthology/P11-5005',
            'paperhash': 'druck|rich_prior_knowledge_in_learning_for_natural_language_processing',
            'title': 'Rich Prior Knowledge in Learning for Natural Language ' 'Processing',
            'venue': 'ACL (Tutorial Abstracts) 2011',
            'venueid': 'dblp.org/conf/ACL/2011',
        },
        'forum': 'HkWL8neu-H',
        'id': 'HkWL8neu-H',
        'invitation': 'dblp.org/-/record',
        'number': 3546,
        'signatures': ['dblp.org'],
    },
}


def load_note_samples() -> Notes:
    note_list = [v for k, v in note_samples.items()]
    sample_notes = {'count': 0, 'notes': note_list}
    notes_str = json.dumps(sample_notes)
    notes_data = json.loads(notes_str)
    notes: Notes = load_notes(notes_data)
    return notes


def create_note_sample(*, title: str) -> Note:
    content_template = NoteContent(
        title='',
        authors=[],
        authorids=[],
        abstract=None,
        html=None,
        venue=None,
        venueid=None,
        _bibtex=None,
        paperhash=None,
        errors=None,
    )
    template = Note(id='', forum='', invitation='', number=0, signatures=[], content=content_template)
    content = dc.replace(content_template, title=title)
    note = dc.replace(template, content=content)
    return note
