from dblp_service.services.author_alignment import align_publications
from tests.dblp_service.openreview_data import create_note_sample
from tests.dblp_service.pub_formats.rdf_tuples.tupledata import create_dblp


# TODO test_pub_align_by_dblpkey
# TODO test_pub_align_by_doi
def test_pub_align_by_title():
    # Correct Alignment
    dblp_my_title = create_dblp(title='My Title')
    note_my_title = create_note_sample(title='My Title')
    aligned = align_publications([note_my_title], [dblp_my_title])
    assert len(aligned.matched_pubs) == 1
    assert len(aligned.unmatched_notes) == 0
    assert len(aligned.unmatched_dblps) == 0

    # Misalignment
    dblp_only_title = create_dblp(title='Dblp Only Title')
    note_only_title = create_note_sample(title='Note Only Title')
    aligned = align_publications([note_only_title], [dblp_only_title])
    assert len(aligned.matched_pubs) == 0
    assert len(aligned.unmatched_notes) == 1
    assert len(aligned.unmatched_dblps) == 1

    # Multiple publications generates same pub_key
    dblp_my_title = create_dblp(title='My Title')
    dblp_my_title2 = create_dblp(title='My Title')
    note_my_title = create_note_sample(title='My Title')
    aligned = align_publications([note_my_title], [dblp_my_title, dblp_my_title2])
    assert len(aligned.matched_pubs) == 1
    assert len(aligned.unmatched_notes) == 0
    assert len(aligned.unmatched_dblps) == 0
    assert len(aligned.warnings) == 1
