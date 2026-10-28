"""AI provider adapters. OpenRouter is preferred when configured; Gemini remains supported."""
import json
import logging
import os
from copy import deepcopy
from urllib import error, request

from google import genai
from google.genai import types

from .config import gemini_api_key, openrouter_api_key
from .models import GeneratedCase

logger = logging.getLogger(__name__)


class AIUnavailable(RuntimeError):
    pass


def gemini_case_schema(model=GeneratedCase):
    """Inline Pydantic definitions and omit keywords unsupported by Gemini."""
    root = model.model_json_schema()
    definitions = root.pop("$defs", {})

    def expand(node):
        if isinstance(node, list):
            return [expand(item) for item in node]
        if not isinstance(node, dict):
            return node
        if "$ref" in node:
            ref = node["$ref"].rsplit("/", 1)[-1]
            resolved = expand(deepcopy(definitions[ref]))
            resolved.update({key: expand(value) for key, value in node.items() if key != "$ref"})
            return resolved
        unsupported = {"$defs", "$schema", "additionalProperties", "minLength", "maxLength"}
        return {key: expand(value) for key, value in node.items() if key not in unsupported}

    return expand(root)


class OpenRouterService:
    """OpenRouter chat-completions adapter with strict local validation downstream."""
    endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key=None, model=None, opener=None):
        self.api_key = openrouter_api_key() if api_key is None else api_key
        self.model = model or os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
        self.opener = opener or request.urlopen

    def _request(self, prompt, max_tokens, response_model=None):
        if not self.api_key:
            raise AIUnavailable("OpenRouter API key is not configured.")
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.4,
        }
        if response_model:
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "strict": True,
                    "schema": response_model.model_json_schema(),
                },
            }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.endpoint,
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with self.opener(req, timeout=90) as response:
                data = json.loads(response.read().decode("utf-8"))
            return (data.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
        except error.HTTPError as exc:
            status = exc.code
            # Never log request headers, which contain the bearer credential.
            logger.warning("OpenRouter request failed (HTTP %s)", status)
            raise AIUnavailable(self._http_message(status)) from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            logger.warning("OpenRouter connection failed (%s)", type(exc).__name__)
            raise AIUnavailable("OpenRouter could not be reached. Check the internet connection and try again.") from exc
        except (ValueError, KeyError, IndexError, TypeError) as exc:
            logger.warning("OpenRouter returned an invalid response (%s)", type(exc).__name__)
            raise AIUnavailable("OpenRouter returned an unusable response. Please try again.") from exc

    @staticmethod
    def _http_message(status):
        if status in (401, 403):
            return "OpenRouter rejected the API key. Check that the key is valid and enabled."
        if status == 429:
            return "OpenRouter is rate limited or out of credits. Wait a little, check your OpenRouter key limits and credits, then try again."
        if status == 404:
            return "The configured OpenRouter model was not found. Check OPENROUTER_MODEL."
        if status in (408, 504):
            return "OpenRouter took too long to respond. Please try again in a moment."
        return "OpenRouter is unavailable right now. Please try again later."

    def generate_json(self, prompt, response_model=GeneratedCase):
        return self._request(prompt, 12000, response_model=response_model)

    def reply(self, prompt):
        return self._request(prompt, 220).strip()


class GeminiService:
    """Google Gemini adapter retained for users who configure Gemini directly."""
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key or gemini_api_key()
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

    def _client(self):
        if not self.api_key:
            raise AIUnavailable("Gemini API key is not configured.")
        return genai.Client(api_key=self.api_key, http_options=types.HttpOptions(timeout=90000))

    def generate_json(self, prompt, response_model=GeneratedCase):
        try:
            config = {"response_mime_type": "application/json", "response_schema": gemini_case_schema(response_model), "max_output_tokens": 12000}
            if self.model.startswith("gemini-3"):
                config["thinking_config"] = types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)
            else:
                config["temperature"] = 0.5
                if self.model.startswith("gemini-2.5"):
                    config["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
            response = self._client().models.generate_content(model=self.model, contents=prompt, config=types.GenerateContentConfig(**config))
            return response.text or ""
        except AIUnavailable:
            raise
        except Exception as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            logger.warning("Gemini generation failed (%s; status=%s)", type(exc).__name__, status)
            if status in (401, 403): message = "Gemini rejected the API key. Check that it is valid and enabled for the Gemini API."
            elif status == 429: message = "Gemini's usage quota was reached. Wait a little or check the selected Google AI Studio project's limits and billing."
            elif status == 404: message = f"The configured Gemini model '{self.model}' was not found. Check GEMINI_MODEL."
            elif status in (408, 504) or "timeout" in type(exc).__name__.lower(): message = "Gemini took too long to build this case. Please try again in a moment."
            else: message = "Gemini is unavailable right now. Please check the app's Gemini setup and try again."
            raise AIUnavailable(message) from exc

    def reply(self, prompt):
        try:
            config = {"max_output_tokens": 220}
            if self.model.startswith("gemini-3"):
                config["thinking_config"] = types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW)
            else:
                config["temperature"] = 0.3
            response = self._client().models.generate_content(model=self.model, contents=prompt, config=types.GenerateContentConfig(**config))
            return (response.text or "").strip()
        except AIUnavailable:
            raise
        except Exception as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            logger.warning("Gemini dialogue failed (%s; status=%s)", type(exc).__name__, status)
            if status == 429:
                raise AIUnavailable("Gemini's usage quota was reached. Wait a little and try again.") from exc
            raise AIUnavailable("Gemini is unavailable right now.") from exc


def get_ai_service():
    """Prefer OpenRouter when configured, otherwise use the Gemini key if present."""
    if openrouter_api_key():
        return OpenRouterService()
    return GeminiService()
