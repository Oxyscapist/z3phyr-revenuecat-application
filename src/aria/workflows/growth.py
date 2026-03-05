from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from aria.config import Settings
from aria.db import Repo
from aria.utils import slugify, write_text


@dataclass(frozen=True)
class GrowthResult:
    name: str
    artifact_path: Path


def _extract_name(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def generate_growth_experiment(
    *,
    settings: Settings,
    repo: Repo,
    llm,
    week_start: date,
) -> GrowthResult:
    prompt = f"""
Design one new weekly growth experiment for RevenueCat awareness among agent builders.

Constraints:
- Human-approval workflow is enabled for external posting.
- Experiment must be realistic for one week.
- Must define success metrics and stop conditions.

Return as markdown:
1. H1 experiment title.
2. Goal.
3. Hypothesis.
4. Experiment design.
5. Instrumentation & metrics.
6. Risks and mitigations.
7. What to do next based on outcomes.
"""
    system_prompt = (
        f"You are {settings.agent_name}, a developer and growth advocate. "
        "Be concrete, measurable, and execution-focused."
    )
    draft = llm.generate(prompt.strip(), system_prompt=system_prompt, temperature=0.2)
    name = _extract_name(draft, fallback="Weekly Growth Experiment")
    file_name = f"{week_start.isoformat()}_{slugify(name)[:80]}.md"
    path = write_text(settings.artifacts_dir / "growth" / file_name, draft.strip() + "\n")
    repo.add_growth_experiment(
        name=name,
        artifact_path=str(path),
        status="planned",
        metadata={"week_start": week_start.isoformat()},
    )
    return GrowthResult(name=name, artifact_path=path)

