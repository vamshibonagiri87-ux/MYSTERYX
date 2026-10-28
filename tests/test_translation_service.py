import json
import pytest

from mysteryx.case_validator import parse_case
from mysteryx.game_service import submit_accusation
from mysteryx.models import Difficulty
from mysteryx.repository import Repository
from mysteryx.translation_service import localized_solved_record, translate_solved_record


class FakeTranslationAI:
    def __init__(self, response):
        self.response=response
        self.calls=0
    def generate_json(self,prompt,response_model):
        self.calls+=1
        assert "తెలుగు" in prompt
        assert response_model.__name__=="SolvedCaseTranslation"
        return json.dumps(self.response,ensure_ascii=False)


def test_solved_record_translation_preserves_clue_ids(case_json,tmp_path):
    repo=Repository(tmp_path/"translated.db")
    sid=repo.save_case(parse_case(case_json,Difficulty.EASY))
    submit_accusation(repo,sid,"S1")
    record=repo.list_solved_cases()[0]
    response={
        "title":"తాళం పెట్టె",
        "chosen_suspect_name":"ఆడా",
        "culprit_name":"ఆడా",
        "full_explanation":"ఆధారాలు ఈ పరిష్కారాన్ని చూపుతున్నాయి.",
        "clues":[{"id":"C1","title":"చిహ్నం 1","description":"ఇక్కడ ఒక ఆధారం కనిపించింది."}],
    }
    ai=FakeTranslationAI(response)
    localized=localized_solved_record(repo,record,"తెలుగు",ai)
    assert localized["title"]=="తాళం పెట్టె"
    assert localized["clues"][0]["id"]=="C1"
    assert ai.calls==1
    cached=localized_solved_record(repo,record,"తెలుగు",ai)
    assert cached==localized
    assert ai.calls==1


def test_translation_rejects_changed_evidence_ids(case_json,tmp_path):
    repo=Repository(tmp_path/"bad-translation.db")
    sid=repo.save_case(parse_case(case_json,Difficulty.EASY))
    submit_accusation(repo,sid,"S1")
    record=repo.list_solved_cases()[0]
    response={
        "title":"రహస్యం",
        "chosen_suspect_name":"ఆడా",
        "culprit_name":"ఆడా",
        "full_explanation":"ఆధారాలు సరిపోతాయి.",
        "clues":[{"id":"WRONG-ID","title":"ఆధారం","description":"వివరణ"}],
    }
    with pytest.raises(ValueError,match="identifiers"):
        translate_solved_record(record,"తెలుగు",FakeTranslationAI(response))
