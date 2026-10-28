import pytest
from mysteryx.models import Difficulty,DIFFICULTY_COUNTS
from mysteryx.case_validator import parse_case,CaseValidationError

@pytest.mark.parametrize("difficulty,counts",[(Difficulty.EASY,(3,5,2)),(Difficulty.MEDIUM,(4,7,3)),(Difficulty.HARD,(5,9,3))])
def test_difficulty_counts(difficulty,counts): assert DIFFICULTY_COUNTS[difficulty][:3]==counts

def test_parse_rejects_malformed_json():
    with pytest.raises(CaseValidationError): parse_case("{bad",Difficulty.EASY)

def test_schema_rejects_missing_and_extra(case_data):
    from mysteryx.models import GeneratedCase
    bad=dict(case_data); bad.pop("story")
    with pytest.raises(Exception): GeneratedCase.model_validate(bad)
    bad=dict(case_data); bad["unexpected"]=1
    with pytest.raises(Exception): GeneratedCase.model_validate(bad)

def test_schema_rejects_invalid_difficulty(case_data):
    from mysteryx.models import GeneratedCase
    case_data["difficulty"]="Extreme"
    with pytest.raises(Exception): GeneratedCase.model_validate(case_data)

def test_gemini_schema_is_inlined_and_supported():
    from mysteryx.ai_service import gemini_case_schema
    import json
    schema=gemini_case_schema()
    serialized=json.dumps(schema)
    assert "$ref" not in serialized
    assert "$defs" not in serialized
    assert "additionalProperties" not in serialized
    assert "case_id" in schema["properties"]
