from __future__ import annotations

from dataclasses import dataclass
import json

import httpx


@dataclass
class OpenAICompatProvider:
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4.1-mini"
    timeout_seconds: int = 60
    name: str = "openai"

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> str:
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        body = {"model": self.model, "messages": messages, "temperature": temperature}
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()

        choices = payload.get("choices", [])
        if not choices:
            raise RuntimeError(f"OpenAI-compatible response has no choices: {json.dumps(payload)}")
        message = choices[0].get("message", {})
        content = message.get("content")
        if isinstance(content, str):
            return content.strip()
        raise RuntimeError("OpenAI-compatible response content is not a plain string.")
