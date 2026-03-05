from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    name: str

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> str: ...
