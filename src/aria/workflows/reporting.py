from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from aria.config import Settings
from aria.db import Repo
from aria.utils import write_text


TARGETS = {
    "content_count": 2,
    "experiment_count": 1,
    "interaction_count": 50,
    "feedback_count": 3,
}


@dataclass(frozen=True)
class WeeklyReportResult:
    artifact_path: Path
    summary: dict


def generate_weekly_report(
    *,
    settings: Settings,
    repo: Repo,
    week_start: date,
) -> WeeklyReportResult:
    week_end = week_start + timedelta(days=7)
    snapshot = repo.metrics_snapshot(week_start.isoformat(), week_end.isoformat())

    achieved = {
        "content_count": snapshot.content_count,
        "experiment_count": snapshot.experiment_count,
        "interaction_count": snapshot.interaction_count,
        "feedback_count": snapshot.feedback_count,
    }

    summary = {
        "week_start": week_start.isoformat(),
        "week_end_exclusive": week_end.isoformat(),
        "targets": TARGETS,
        "achieved": achieved,
    }

    lines = [
        "# Weekly Async Check-in",
        "",
        f"- Agent: {settings.agent_name}",
        f"- Week start: {week_start.isoformat()}",
        f"- Week end (exclusive): {week_end.isoformat()}",
        "",
        "| KPI | Target | Achieved | Status |",
        "|-----|--------|----------|--------|",
    ]
    for key, target in TARGETS.items():
        value = achieved[key]
        status = "On Track" if value >= target else "At Risk"
        label = key.replace("_", " ")
        lines.append(f"| {label} | {target} | {value} | {status} |")

    lines.extend(
        [
            "",
            "## Notes",
            "- External community publishing remains human-approved by design.",
            "- This report can be posted directly in weekly async check-ins.",
        ]
    )

    path = write_text(
        settings.artifacts_dir / "reports" / f"{week_start.isoformat()}_weekly_report.md",
        "\n".join(lines) + "\n",
    )
    repo.add_weekly_report(
        week_start=week_start.isoformat(),
        week_end=week_end.isoformat(),
        artifact_path=str(path),
        summary=summary,
    )
    return WeeklyReportResult(artifact_path=path, summary=summary)

