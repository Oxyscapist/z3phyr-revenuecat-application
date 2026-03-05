from __future__ import annotations

from dataclasses import dataclass
import json

import httpx


@dataclass
class GeminiProvider:
    api_key: str
    model: str = "gemini-2.5-flash-lite"
    timeout_seconds: int = 60
    name: str = "gemini"

    def _extract_text(self, payload: dict) -> str:
        candidates = payload.get("candidates", [])
        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {json.dumps(payload)}")

        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        chunks: list[str] = []
        for part in parts:
            text = part.get("text")
            if text:
                chunks.append(text)
        if chunks:
            return "\n".join(chunks).strip()

        finish_reason = candidates[0].get("finishReason", "unknown")
        raise RuntimeError(f"Gemini response had no text output. finishReason={finish_reason}")

    def _try_model(
        self, client: httpx.Client, model: str, prompt: str, system_prompt: str | None, temperature: float
    ) -> str:
        endpoint = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        )
        headers = {"Content-Type": "application/json"}
        body: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}
        response = client.post(
            endpoint, params={"key": self.api_key}, headers=headers, json=body
        )
        if response.status_code == 404:
            raise FileNotFoundError(f"Model not found: {model}")
        response.raise_for_status()
        payload = response.json()
        return self._extract_text(payload)

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        fallback_models = []
        if self.model == "gemini-2.5-flash-lite":
            fallback_models = ["gemini-2.5-flash", "gemini-2.0-flash-lite", "gemini-2.0-flash"]
        model_candidates = [self.model] + fallback_models

        with httpx.Client(timeout=self.timeout_seconds) as client:
            last_error: Exception | None = None
            for model in model_candidates:
                try:
                    return self._try_model(client, model, prompt, system_prompt, temperature)
                except FileNotFoundError as err:
                    last_error = err
                    continue
            raise RuntimeError(
                f"Unable to call Gemini model. Checked: {', '.join(model_candidates)}"
            ) from last_error
