from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import json

from aria.config import Settings
from aria.db import Repo
from aria.utils import monday_for_week, write_text


@dataclass(frozen=True)
class DashboardResult:
    markdown_path: Path
    json_path: Path


def generate_dashboard(
    *,
    settings: Settings,
    repo: Repo,
    week_start: str | None = None,
    output_stem: str = "latest",
) -> DashboardResult:
    week_start_date = monday_for_week(week_start)
    week_end_date = week_start_date + timedelta(days=7)
    snapshot = repo.metrics_snapshot(week_start_date.isoformat(), week_end_date.isoformat())
    quality = repo.quality_summary(week_start_date.isoformat(), week_end_date.isoformat())
    runs = repo.recent_runs(limit=10)
    publish_counts = repo.publication_status_counts()
    prompts = repo.list_prompt_registry(limit=10)
    last_run_memory = repo.get_memory("last_weekly_run")

    payload = {
        "week_start": week_start_date.isoformat(),
        "week_end_exclusive": week_end_date.isoformat(),
        "kpis": {
            "content_count": snapshot.content_count,
            "experiment_count": snapshot.experiment_count,
            "interaction_count": snapshot.interaction_count,
            "feedback_count": snapshot.feedback_count,
        },
        "quality": quality,
        "publish_counts": publish_counts,
        "recent_runs": runs,
        "recent_prompts": prompts,
        "last_run_memory": last_run_memory,
    }

    dashboard_dir = settings.artifacts_dir / "dashboard"
    markdown_path = dashboard_dir / f"{output_stem}.md"
    json_path = dashboard_dir / f"{output_stem}.json"

    md_lines = [
        "# ARIA Observability Dashboard",
        "",
        f"- Week start: {payload['week_start']}",
        f"- Week end (exclusive): {payload['week_end_exclusive']}",
        "",
        "## KPI Snapshot",
        f"- Content: {snapshot.content_count}",
        f"- Growth experiments: {snapshot.experiment_count}",
        f"- Community interactions: {snapshot.interaction_count}",
        f"- Product feedback: {snapshot.feedback_count}",
        "",
        "## Quality Summary",
        f"- Global average: {quality['global_avg']}",
        f"- Scored artifacts: {quality['total_count']}",
        "",
        "## Publish Queue Status",
    ]
    if publish_counts:
        for status, count in sorted(publish_counts.items()):
            md_lines.append(f"- {status}: {count}")
    else:
        md_lines.append("- No publish queue items.")

    md_lines.extend(
        [
            "",
            "## Recent Runs",
            "| id | command | status | started_at | finished_at | provider |",
            "|----|---------|--------|------------|-------------|----------|",
        ]
    )
    if runs:
        for run in runs:
            md_lines.append(
                f"| {run.get('id')} | {run.get('command')} | {run.get('status')} | "
                f"{run.get('started_at')} | {run.get('finished_at') or ''} | {run.get('provider')} |"
            )
    else:
        md_lines.append("| - | - | - | - | - | - |")

    md_lines.extend(
        [
            "",
            f"JSON payload: `{json_path.name}`",
        ]
    )

    write_text(markdown_path, "\n".join(md_lines) + "\n")
    write_text(json_path, json.dumps(payload, indent=2) + "\n")
    return DashboardResult(markdown_path=markdown_path, json_path=json_path)
