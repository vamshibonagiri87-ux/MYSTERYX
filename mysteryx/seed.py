"""Deterministic known-good case for local development and tests."""
from .models import GeneratedCase

SEED_CASE = {
    "case_id":"seed-draft","title":"The Conservatory Locket","premise":"A silver locket disappears from a locked conservatory during a student exhibition.",
    "difficulty":"Easy","story":"At the end of the exhibition, the conservatory cabinet is found open and its silver locket missing.",
    "suspects":[
        {"id":"S1","name":"Ada Vale","profile":"A careful student archivist who catalogued the display.","motive":"Ada hoped to keep the locket's story from being forgotten.","public_alibi":"Ada says she checked the display shortly before the guests arrived.","private_truth":"Ada noticed the cabinet key ring was damp but did not touch the locket."},
        {"id":"S2","name":"Ben Rowan","profile":"A groundskeeper familiar with the conservatory doors.","motive":"Ben is worried the school will sell the old collection.","public_alibi":"Ben says he was securing the garden doors when the locket vanished.","private_truth":"Ben was outside in the rain and never entered the display room."},
        {"id":"S3","name":"Cora Lin","profile":"A visiting musician invited to the exhibition.","motive":"Cora admired the locket's carved musical motif.","public_alibi":"Cora says she stayed by the piano during the final song.","private_truth":"Cora left the room briefly to retrieve a music folder."}],
    "clues":[
        {"id":"C1","title":"Damp Key Ring","description":"The cabinet key ring is wet although the cabinet room stayed dry.","details":"A thin crescent of garden soil clings to the ring's leather tag.","implicates_suspect_ids":["S2"],"solution_relevance":"The key ring was carried in from the garden during the brief unlocked interval."},
        {"id":"C2","title":"Cabinet Register","description":"The register shows the cabinet was secure at the start of the exhibition.","details":"The final check is initialled by the archivist.","implicates_suspect_ids":["S1"],"solution_relevance":"Confirms the item was present after the earlier cataloguing."},
        {"id":"C3","title":"Piano Bench","description":"A music folder rests beside the piano bench.","details":"The folder was placed there before the final song.","implicates_suspect_ids":["S3"],"solution_relevance":"Supports Cora's account of remaining near the piano."},
        {"id":"C4","title":"Garden Door","description":"The garden door latch has fresh rainwater on its outer edge.","details":"The wet marks lead back toward the covered path.","implicates_suspect_ids":["S2"],"solution_relevance":"Establishes a plausible route from the garden to the cabinet."},
        {"id":"C5","title":"Display Cloth","description":"The velvet display cloth is folded neatly beside the empty stand.","details":"No fibers or damage suggest the cabinet was forced.","implicates_suspect_ids":["S1","S3"],"solution_relevance":"Shows the cabinet was opened with its key, not broken."}],
    "hints":[{"id":"H1","text":"Compare the wet trace with each suspect's route.","reveal_level":1},{"id":"H2","text":"The key was used; look for a connection between the cabinet and the garden.","reveal_level":2}],
    "solution":{"culprit_id":"S2","reasoning":"The damp key ring and garden route establish Ben's opportunity.","supporting_clue_ids":["C1","C4","C5"],"full_explanation":"Ben entered from the garden during the exhibition and used the cabinet key. C1's damp soil on the ring and C4's fresh rainwater establish the route, while C5 confirms the cabinet was opened without force. Ada's register check and Cora's folder by the piano support their stated timelines."},
    "timeline":[{"time":"17:30","event":"Ada confirms the locket is in the locked cabinet."},{"time":"18:10","event":"Rain begins along the garden path."},{"time":"18:25","event":"The cabinet is discovered open after the exhibition."}]}

def seed_case(): return GeneratedCase.model_validate(SEED_CASE)
