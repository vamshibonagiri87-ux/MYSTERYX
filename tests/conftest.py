import json, pytest
from mysteryx.models import Difficulty, DIFFICULTY_COUNTS

@pytest.fixture
def case_data():
    difficulty=Difficulty.EASY; ns,nc,nh,_=DIFFICULTY_COUNTS[difficulty]
    return {"case_id":"draft","title":"The Missing Locket","premise":"A locket vanishes from the conservatory during a school exhibition.","difficulty":"Easy","story":"A locked cabinet stands open after the exhibition.",
        "suspects":[{"id":f"S{i+1}","name":["Ada","Ben","Cora"][i],"profile":"A visitor with a distinct connection to the conservatory.","motive":"Each has a personal reason to be curious about the locket.","public_alibi":"They describe where they were during the exhibition.","private_truth":f"Private consistency note for suspect {i+1}."} for i in range(ns)],
        "clues":[{"id":f"C{i+1}","title":f"Trace {i+1}","description":"A small physical detail is found near the cabinet.","details":"The detail is consistent with the event timeline.","implicates_suspect_ids":["S1" if i==0 else f"S{(i%ns)+1}"],"solution_relevance":"It supports the established timeline."} for i in range(nc)],
        "hints":[{"id":f"H{i+1}","text":f"Compare clue {i+1} with the timeline.","reveal_level":i+1} for i in range(nh)],
        "solution":{"culprit_id":"S1","reasoning":"The timeline is inconsistent with the physical trace.","supporting_clue_ids":["C1"],"full_explanation":"The stored timeline and C1 support the solution."},"timeline":[{"time":"18:00","event":"The cabinet was checked before the exhibition."}]}

@pytest.fixture
def case_json(case_data): return json.dumps(case_data)
