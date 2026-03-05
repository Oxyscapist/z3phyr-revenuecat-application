from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from aria.config import Settings
from aria.db import Repo
from aria.utils import slugify, write_text


@dataclass(frozen=True)
class FeedbackResult:
    title: str
    severity: str
    artifact_path: Path


def _extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        if line.strip().startswith("# "):
            return line.strip()[2:]
    return fallback


def _extract_severity(markdown: str) -> str:
    match = re.search(r"(?im)^severity\s*:\s*(high|medium|low)\s*$", markdown)
    if match:
        return match.group(1).lower()
    return "medium"


def generate_feedback_batch(
    *,
    settings: Settings,
    repo: Repo,
    llm,
    week_start: date,
    count: int = 3,
) -> list[FeedbackResult]:
    feedback_dir = settings.artifacts_dir / "feedback"
    results: list[FeedbackResult] = []
    for idx in range(count):
        prompt = f"""
Create one structured product feedback memo for RevenueCat from an agentic builder perspective.

Output format (markdown):
1. H1 title.
2. Severity: high|medium|low (single line).
3. Problem observed.
4. Who it impacts.
5. Reproduction steps.
6. Recommended product improvement.
7. Expected impact.
8. Evidence to collect.
"""
        system_prompt = (
            f"You are {settings.agent_name}, acting as an autonomous developer advocate and growth operator. "
            "Focus on actionable product feedback."
        )
        draft = llm.generate(prompt.strip(), system_prompt=system_prompt, temperature=0.2)
        title = _extract_title(draft, fallback=f"Product Feedback {idx + 1}")
        severity = _extract_severity(draft)
        path = write_text(
            feedback_dir / f"{week_start.isoformat()}_{idx+1:02d}_{slugify(title)[:80]}.md",
            draft.strip() + "\n",
        )
        repo.add_feedback(
            title=title,
            severity=severity,
            artifact_path=str(path),
            status="submitted",
            metadata={"week_start": week_start.isoformat()},
        )
        results.append(FeedbackResult(title=title, severity=severity, artifact_path=path))
    return results

