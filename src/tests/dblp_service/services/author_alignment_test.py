from dblp_service.open_exchange.note_schemas import Notes
from dblp_service.services.author_alignment import align_pubs, print_aligned
from tests.dblp_service.openreview_data import load_note_samples
from tests.dblp_service.pub_formats.rdf_tuples.tupledata import load_repr_sample

def test_align_graphs():
    pub_repr = load_repr_sample()
    notes: Notes = load_note_samples()
    aligned = align_pubs(notes.notes, [pub_repr])
    print_aligned(aligned)
