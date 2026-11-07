"""Minimal Ollama client for local, structured model inference."""

from __future__ import annotations

import json
from typing import Any, TypeVar
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from pydantic import BaseModel, ValidationError

from evidence_graph.storage.cache import SQLiteCache


OutputModel = TypeVar("OutputModel", bound=BaseModel)


class LLMError(RuntimeError):
    """Raised when a local model cannot produce a valid response."""


class OllamaClient:
    def __init__(
        self,
        model: str = "qwen3:8b",
        base_url: str = "http://localhost:11434",
        timeout: float = 120.0,
        temperature: float = 0.0,
        cache: SQLiteCache | None = None,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.temperature = temperature
        self.cache = cache

    def generate_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        output_model: type[OutputModel],
    ) -> OutputModel:
        payload = {
            "model": self.model,
            "stream": False,
            "format": output_model.model_json_schema(),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {"temperature": self.temperature},
        }
        response = self._post("/api/chat", payload)
        try:
            content = response["message"]["content"]
            return output_model.model_validate_json(content)
        except (KeyError, TypeError, ValidationError, json.JSONDecodeError) as exc:
            raise LLMError("Ollama returned invalid structured output") from exc

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        cache_inputs = {"base_url": self.base_url, "path": path, "payload": payload}
        cached = self.cache.get("ollama.analysis.v1", cache_inputs) if self.cache else None
        if cached is not None:
            return cached
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
            if self.cache:
                self.cache.set("ollama.analysis.v1", cache_inputs, result)
            return result
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise LLMError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
        except (URLError, TimeoutError) as exc:
            raise LLMError(
                f"Could not reach Ollama at {self.base_url}. Is `ollama serve` running?"
            ) from exc
        except json.JSONDecodeError as exc:
            raise LLMError("Ollama returned a non-JSON response") from exc
