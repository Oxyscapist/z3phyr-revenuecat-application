from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from aria.config import Settings
from aria.db import Repo
from aria.prompts import load_prompt, render_template
from aria.quality import score_file
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
    fallback_system = (
        "You are a developer and growth advocate focused on measurable execution."
    )
    fallback_user_template = """
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
    prompt_spec = load_prompt(
        settings=settings,
        prompt_name="growth_experiment",
        fallback_system_prompt=fallback_system,
        fallback_user_template=fallback_user_template,
    )
    repo.register_prompt(prompt_spec.name, prompt_spec.version, prompt_spec.source_path)
    prompt = render_template(
        prompt_spec.user_template,
        {
            "agent_name": settings.agent_name,
            "tone": settings.tone,
            "positioning": settings.positioning,
        },
    )
    draft = llm.generate(
        prompt.strip(), system_prompt=prompt_spec.system_prompt, temperature=0.2
    )
    name = _extract_name(draft, fallback="Weekly Growth Experiment")
    file_name = f"{week_start.isoformat()}_{slugify(name)[:80]}.md"
    path = write_text(settings.artifacts_dir / "growth" / file_name, draft.strip() + "\n")
    quality = score_file(repo, artifact_type="growth", artifact_path=path)
    repo.add_growth_experiment(
        name=name,
        artifact_path=str(path),
        status="planned",
        metadata={
            "week_start": week_start.isoformat(),
            "prompt_name": prompt_spec.name,
            "prompt_version": prompt_spec.version,
            "quality_score": quality.score,
        },
    )
    return GrowthResult(name=name, artifact_path=path)

