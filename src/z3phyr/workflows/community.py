from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from z3phyr.config import Settings
from z3phyr.db import Repo
from z3phyr.utils import write_text


CHANNELS = ["X", "GitHub", "Discord", "Forums"]
THEMES = [
    "RevenueCat SDK integration",
    "Paywall iteration strategy",
    "Subscription churn diagnostics",
    "Charts API instrumentation",
    "Cross-platform purchase flow QA",
]
ACTION_TYPES = [
    "Answer an implementation question with a code sample",
    "Post a short teardown of a growth funnel issue",
    "Share a measured experiment idea with success criteria",
    "Comment with a concrete debugging checklist",
    "Offer a reproducible example repo snippet",
]


@dataclass(frozen=True)
class CommunityQueueResult:
    artifact_path: Path
    count: int


def build_interaction_queue(
    *,
    settings: Settings,
    repo: Repo,
    week_start: date,
    target_count: int = 50,
) -> CommunityQueueResult:
    lines = [
        "# Weekly Community Interaction Queue",
        "",
        f"- Agent: {settings.agent_name}",
        f"- Week start: {week_start.isoformat()}",
        f"- Target interactions: {target_count}",
        "- Status: Human approval required before publishing",
        "",
        "| # | Channel | Draft target | Draft interaction idea |",
        "|---|---------|--------------|------------------------|",
    ]

    for i in range(target_count):
        channel = CHANNELS[i % len(CHANNELS)]
        theme = THEMES[i % len(THEMES)]
        action = ACTION_TYPES[i % len(ACTION_TYPES)]
        target = f"{channel.lower()}-thread-{i+1:02d}"
        message = f"{action} focused on {theme}. Ask one clarifying follow-up question."
        repo.add_interaction(
            channel=channel,
            target=target,
            draft_message=message,
            status="needs_human_approval",
            metadata={"week_start": week_start.isoformat()},
        )
        safe_message = message.replace("|", "\\|")
        lines.append(f"| {i+1} | {channel} | `{target}` | {safe_message} |")

    path = write_text(
        settings.artifacts_dir / "community" / f"{week_start.isoformat()}_interaction_queue.md",
        "\n".join(lines) + "\n",
    )
    return CommunityQueueResult(artifact_path=path, count=target_count)
