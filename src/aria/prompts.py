from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from aria.config import Settings


@dataclass(frozen=True)
class PromptSpec:
    name: str
    version: str
    system_prompt: str
    user_template: str
    source_path: str


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def render_template(template: str, values: dict[str, str]) -> str:
    return template.format_map(_SafeFormatDict(values))


def _load_prompt_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError(f"Prompt file {path} is not a JSON object.")
    return data


def load_prompt(
    *,
    settings: Settings,
    prompt_name: str,
    fallback_system_prompt: str,
    fallback_user_template: str,
) -> PromptSpec:
    path = settings.prompts_dir / f"{prompt_name}.json"
    if not path.exists():
        return PromptSpec(
            name=prompt_name,
            version="fallback-1",
            system_prompt=fallback_system_prompt.strip(),
            user_template=fallback_user_template.strip(),
            source_path="<fallback>",
        )

    data = _load_prompt_file(path)
    system_prompt = str(data.get("system_prompt", fallback_system_prompt)).strip()
    user_template = str(data.get("user_template", fallback_user_template)).strip()
    version = str(data.get("version", "1"))
    return PromptSpec(
        name=str(data.get("name", prompt_name)),
        version=version,
        system_prompt=system_prompt,
        user_template=user_template,
        source_path=str(path),
    )
