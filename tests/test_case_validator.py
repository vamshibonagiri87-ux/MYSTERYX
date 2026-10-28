import pytest
from mysteryx.models import Difficulty
from mysteryx.case_validator import parse_case,CaseValidationError,public_case

def test_valid_case_and_private_omission(case_json):
    case=parse_case(case_json,Difficulty.EASY)
    player=public_case(case)
    assert "solution" not in player and "private_truth" not in str(player)
    assert player["clues"]==[]

@pytest.mark.parametrize("mutation",["duplicate_suspect","broken_culprit","broken_clue","duplicate_clue"])
def test_semantic_references_rejected(case_data,mutation):
    if mutation=="duplicate_suspect": case_data["suspects"][1]["id"]="S1"
    elif mutation=="broken_culprit": case_data["solution"]["culprit_id"]="SX"
    elif mutation=="broken_clue": case_data["solution"]["supporting_clue_ids"]=["CX"]
    else: case_data["clues"][1]["id"]="C1"
    import json
    with pytest.raises(CaseValidationError): parse_case(json.dumps(case_data),Difficulty.EASY)
