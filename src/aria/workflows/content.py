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
class ContentResult:
    title: str
    topic: str
    artifact_path: Path


DEFAULT_TOPICS = [
    "How autonomous agents can ship RevenueCat paywalls in under one hour",
    "Using RevenueCat webhooks to let AI agents trigger lifecycle automation",
    "Agent-safe subscription analytics with RevenueCat Charts API",
    "Programmatic SKU testing for mobile subscriptions using RevenueCat",
]


def _extract_title(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        match = re.match(r"^\s*#{1,3}\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return fallback


def generate_content_batch(
    *,
    settings: Settings,
    repo: Repo,
    llm,
    count: int,
    week_start: date,
) -> list[ContentResult]:
    fallback_system = (
        "You are an autonomous developer and growth advocate. "
        "Write for technical builders who value precise implementation details."
    )
    fallback_user_template = """
Create a technical content draft for developer and growth audiences.

Context:
- Agent identity: {agent_name}
- Tone: {tone}
- Positioning: {positioning}
- Topic: {topic}
- Objective: teach agentic builders how to use RevenueCat pragmatically

Output format requirements:
1. Start with a markdown H1 title.
2. Include sections: Why this matters, Step-by-step implementation, Metrics to track, Pitfalls, Next action.
3. Keep it practical and concrete.
4. Include at least one code block and one KPI checklist.
"""
    prompt_spec = load_prompt(
        settings=settings,
        prompt_name="content_draft",
        fallback_system_prompt=fallback_system,
        fallback_user_template=fallback_user_template,
    )
    repo.register_prompt(prompt_spec.name, prompt_spec.version, prompt_spec.source_path)

    content_dir = settings.artifacts_dir / "content"
    results: list[ContentResult] = []
    for idx in range(count):
        topic = DEFAULT_TOPICS[idx % len(DEFAULT_TOPICS)]
        prompt = render_template(
            prompt_spec.user_template,
            {
                "agent_name": settings.agent_name,
                "tone": settings.tone,
                "positioning": settings.positioning,
                "topic": topic,
            },
        )
        draft = llm.generate(
            prompt.strip(), system_prompt=prompt_spec.system_prompt, temperature=0.25
        )
        title = _extract_title(draft, fallback=f"Draft on {topic}")
        file_name = f"{week_start.isoformat()}_{idx+1:02d}_{slugify(title)[:80]}.md"
        path = write_text(content_dir / file_name, draft.strip() + "\n")
        quality = score_file(repo, artifact_type="content", artifact_path=path)
        repo.add_content(
            title=title,
            topic=topic,
            artifact_path=str(path),
            metadata={
                "week_start": week_start.isoformat(),
                "prompt_name": prompt_spec.name,
                "prompt_version": prompt_spec.version,
                "quality_score": quality.score,
            },
        )
        results.append(ContentResult(title=title, topic=topic, artifact_path=path))
    return results

