import json
import pytest
from mysteryx.repository import Repository
from mysteryx.models import GeneratedCase,Difficulty
from mysteryx.case_validator import parse_case
from mysteryx.game_service import discover_clue,request_hint,submit_accusation
from mysteryx.case_generator import generate_case,GenerationError
from mysteryx.seed import seed_case
from mysteryx.ai_service import AIUnavailable

class FakeAI:
    def __init__(self, values): self.values=list(values)
    def generate_json(self,prompt):
        value=self.values.pop(0)
        if isinstance(value,Exception): raise value
        return value

def test_generate_retry_then_save(case_json,tmp_path):
    case=generate_case("A priceless diamond vanishes from the old mansion during a storm.",Difficulty.EASY,FakeAI(["no",case_json]))
    repo=Repository(tmp_path/"game.db"); sid=repo.save_case(case)
    assert repo.get_game(sid)["case"]["title"]=="The Missing Locket"

def test_generated_case_saves_selected_story_language(case_json,tmp_path):
    class PromptAI(FakeAI):
        prompt=""
        def generate_json(self,prompt):
            self.prompt=prompt
            return super().generate_json(prompt)
    ai=PromptAI([case_json])
    case=generate_case("A priceless diamond vanishes from the old mansion during a storm.",Difficulty.EASY,ai,language="తెలుగు")
    assert "తెలుగు" in ai.prompt
    repo=Repository(tmp_path/"telugu.db"); sid=repo.save_case(case,language="తెలుగు")
    assert repo.get_game(sid)["case"]["language"]=="తెలుగు"

def test_solved_history_contains_only_completed_cases(case_json,tmp_path):
    repo=Repository(tmp_path/"history.db")
    sid=repo.save_case(parse_case(case_json,Difficulty.EASY))
    assert repo.list_solved_cases()==[]
    result=submit_accusation(repo,sid,"S1")
    history=repo.list_solved_cases()
    assert len(history)==1
    assert history[0]["session_id"]==sid
    assert history[0]["result"]["final_score"]==result["final_score"]
    assert history[0]["culprit"]["id"]=="S1"

def test_invalid_generation_fails_safely():
    import pytest
    with pytest.raises(GenerationError): generate_case("A priceless diamond vanishes from the old mansion during a storm.",Difficulty.EASY,FakeAI(["bad","bad","bad"]))

def test_generation_error_explains_gemini_setup():
    import pytest
    with pytest.raises(GenerationError,match="API key is not configured"):
        generate_case("A priceless diamond vanishes from the old mansion during a storm.",Difficulty.EASY,FakeAI([AIUnavailable("Gemini API key is not configured.")]))

def test_missing_key_error_is_not_hidden(monkeypatch):
    from mysteryx import ai_service
    monkeypatch.setattr(ai_service,"gemini_api_key",lambda:None)
    with pytest.raises(AIUnavailable,match="API key is not configured"):
        ai_service.GeminiService().generate_json("{}");

def test_gemini_client_is_retained_during_request(monkeypatch):
    from mysteryx import ai_service
    class Models:
        captured=None
        def generate_content(self,**kwargs):
            self.captured=kwargs
            return type("Response",(),{"text":"{}"})()
    class Client:
        def __init__(self,**kwargs): self.models=Models()
    monkeypatch.setattr(ai_service.genai,"Client",Client)
    service=ai_service.GeminiService(api_key="test-key",model="gemini-3.5-flash-lite")
    assert service.model=="gemini-3.5-flash-lite"
    assert service.generate_json("prompt")=="{}"

def test_seed_case_is_valid():
    from mysteryx.case_validator import parse_case
    case=seed_case()
    assert parse_case(case.model_dump_json(),Difficulty.EASY).solution.culprit_id=="S2"

def test_flow_unique_discovery_hint_and_idempotent_accusation(case_json,tmp_path):
    repo=Repository(tmp_path/"flow.db"); sid=repo.save_case(parse_case(case_json,Difficulty.EASY))
    assert discover_clue(repo,sid,"C1") is True
    assert discover_clue(repo,sid,"C1") is False
    assert request_hint(repo,sid)["id"]=="H1"
    assert request_hint(repo,sid)["id"]=="H2"
    assert request_hint(repo,sid) is None
    result=submit_accusation(repo,sid,"S1")
    again=submit_accusation(repo,sid,"S2")
    assert result["final_score"]==85
    assert again["final_score"]==result["final_score"] and again["selected_suspect_id"]=="S1"
    assert repo.get_game(sid)["solution"]["culprit_id"]=="S1"
    reopened=Repository(repo.path).get_game(sid)
    assert reopened["discoveries"]==["C1"] and reopened["result"]["final_score"]==85
