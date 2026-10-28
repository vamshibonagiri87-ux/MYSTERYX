import json

from mysteryx import ai_service
from mysteryx.models import GeneratedCase


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self.payload).encode()


def test_openrouter_sends_structured_output_and_returns_text():
    captured = {}

    def opener(req, timeout):
        captured["url"] = req.full_url
        captured["authorization"] = req.get_header("Authorization")
        captured["timeout"] = timeout
        captured["payload"] = json.loads(req.data)
        return FakeResponse({"choices": [{"message": {"content": '{"ok":true}'}}]})

    service = ai_service.OpenRouterService(api_key="test-key", model="google/gemini-2.5-flash", opener=opener)
    assert service.generate_json("return json") == '{"ok":true}'
    assert captured["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert captured["authorization"] == "Bearer test-key"
    assert captured["timeout"] == 90
    assert captured["payload"]["model"] == "google/gemini-2.5-flash"
    schema = captured["payload"]["response_format"]["json_schema"]
    assert schema["strict"] is True
    assert schema["schema"]["title"] == GeneratedCase.__name__


def test_openrouter_missing_key_is_clear():
    import pytest
    service = ai_service.OpenRouterService(api_key="", opener=lambda *args, **kwargs: None)
    with pytest.raises(ai_service.AIUnavailable, match="OpenRouter API key is not configured"):
        service.reply("hello")


def test_provider_factory_prefers_openrouter(monkeypatch):
    monkeypatch.setattr(ai_service, "openrouter_api_key", lambda: "router-key")
    monkeypatch.setattr(ai_service, "gemini_api_key", lambda: "gemini-key")
    assert isinstance(ai_service.get_ai_service(), ai_service.OpenRouterService)


def test_provider_factory_keeps_gemini_fallback(monkeypatch):
    monkeypatch.setattr(ai_service, "openrouter_api_key", lambda: None)
    monkeypatch.setattr(ai_service, "gemini_api_key", lambda: "gemini-key")
    assert isinstance(ai_service.get_ai_service(), ai_service.GeminiService)
