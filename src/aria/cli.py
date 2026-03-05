from __future__ import annotations

import argparse
from datetime import timedelta
import json
from pathlib import Path
import sys

from aria.config import Settings
from aria.db import Repo
from aria.llm.factory import build_provider
from aria.utils import ensure_dir, monday_for_week
from aria.workflows.application import (
    ApplicationLetterInput,
    build_public_application_letter,
)
from aria.workflows.community import build_interaction_queue
from aria.workflows.content import generate_content_batch
from aria.workflows.dashboard import generate_dashboard
from aria.workflows.feedback import generate_feedback_batch
from aria.workflows.growth import generate_growth_experiment
from aria.workflows.publishing import (
    approve_publication,
    execute_publication,
    queue_publication,
)
from aria.workflows.reporting import generate_weekly_report


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aria",
        description="ARIA autonomous revenue intelligence agent",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_cmd = subparsers.add_parser("init", help="Initialize directories and local database")
    init_cmd.add_argument("--root", default=".", help="Project root path")

    run_cmd = subparsers.add_parser(
        "run-weekly", help="Run one weekly cycle (content, growth, community, feedback, report)"
    )
    run_cmd.add_argument("--root", default=".", help="Project root path")
    run_cmd.add_argument("--week-start", default=None, help="Week start date YYYY-MM-DD")
    run_cmd.add_argument("--provider", default=None, help="Override provider: gemini|mock|openai")
    run_cmd.add_argument("--content-count", type=int, default=2)
    run_cmd.add_argument("--interaction-target", type=int, default=50)
    run_cmd.add_argument("--feedback-count", type=int, default=3)
    run_cmd.add_argument(
        "--queue-content-gists",
        action="store_true",
        help="Queue generated content artifacts for github_gist publishing.",
    )

    letter_cmd = subparsers.add_parser(
        "build-application-letter", help="Generate public application letter markdown"
    )
    letter_cmd.add_argument("--root", default=".", help="Project root path")
    letter_cmd.add_argument("--repo-url", required=True, help="Public repository URL")
    letter_cmd.add_argument(
        "--operator-name", default="<OPERATOR_FULL_NAME>", help="Operator full name"
    )
    letter_cmd.add_argument(
        "--operator-location", default="<CITY, COUNTRY>", help="Operator work location"
    )
    letter_cmd.add_argument(
        "--output",
        default="artifacts/application/public_application_letter.md",
        help="Output markdown path",
    )

    dashboard_cmd = subparsers.add_parser(
        "dashboard", help="Generate observability dashboard markdown and JSON"
    )
    dashboard_cmd.add_argument("--root", default=".", help="Project root path")
    dashboard_cmd.add_argument("--week-start", default=None, help="Week start date YYYY-MM-DD")
    dashboard_cmd.add_argument("--output-stem", default="latest", help="Output file stem")

    queue_cmd = subparsers.add_parser(
        "queue-publish", help="Queue a publication artifact for human approval"
    )
    queue_cmd.add_argument("--root", default=".", help="Project root path")
    queue_cmd.add_argument("--channel", required=True, choices=["github_gist", "x_post"])
    queue_cmd.add_argument("--artifact", required=True, help="Path to markdown artifact")
    queue_cmd.add_argument("--title", required=True, help="Publication title")
    queue_cmd.add_argument(
        "--metadata-json", default="{}", help="Optional JSON metadata object string"
    )

    list_cmd = subparsers.add_parser("list-publish", help="List publication queue items")
    list_cmd.add_argument("--root", default=".", help="Project root path")
    list_cmd.add_argument("--status", default=None, help="Filter by status")
    list_cmd.add_argument("--limit", type=int, default=50)

    approve_cmd = subparsers.add_parser(
        "approve-publish", help="Approve a queued publication item"
    )
    approve_cmd.add_argument("--root", default=".", help="Project root path")
    approve_cmd.add_argument("--id", type=int, required=True)
    approve_cmd.add_argument("--approved-by", required=True, help="Approver identity")

    execute_cmd = subparsers.add_parser(
        "execute-publish", help="Execute a previously approved publication item"
    )
    execute_cmd.add_argument("--root", default=".", help="Project root path")
    execute_cmd.add_argument("--id", type=int, required=True)

    return parser.parse_args(argv)


def _settings(root: str) -> Settings:
    return Settings.from_env(Path(root).resolve())


def _init_environment(settings: Settings) -> Repo:
    ensure_dir(settings.data_dir)
    ensure_dir(settings.artifacts_dir)
    ensure_dir(settings.prompts_dir)
    repo = Repo(settings.db_path)
    return repo


def _cmd_init(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    print("Initialized ARIA environment")
    print(f"data_dir={settings.data_dir}")
    print(f"artifacts_dir={settings.artifacts_dir}")
    print(f"prompts_dir={settings.prompts_dir}")
    print(f"db_path={repo.db_path}")
    return 0


def _cmd_run_weekly(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    provider = build_provider(settings, force_provider=args.provider)
    week_start = monday_for_week(args.week_start)
    run_id = repo.start_run(
        command="run-weekly",
        provider=provider.name,
        model=settings.model,
        week_start=week_start.isoformat(),
    )

    print(f"Running weekly cycle for {week_start.isoformat()} with provider={provider.name}")

    try:
        content_results = generate_content_batch(
            settings=settings,
            repo=repo,
            llm=provider,
            count=args.content_count,
            week_start=week_start,
        )
        growth_result = generate_growth_experiment(
            settings=settings,
            repo=repo,
            llm=provider,
            week_start=week_start,
        )
        community_result = build_interaction_queue(
            settings=settings,
            repo=repo,
            week_start=week_start,
            target_count=args.interaction_target,
        )
        feedback_results = generate_feedback_batch(
            settings=settings,
            repo=repo,
            llm=provider,
            week_start=week_start,
            count=args.feedback_count,
        )
        report_result = generate_weekly_report(settings=settings, repo=repo, week_start=week_start)

        queued_publications = 0
        if args.queue_content_gists:
            for content in content_results:
                queue_publication(
                    repo=repo,
                    channel="github_gist",
                    title=f"ARIA Content: {content.title}",
                    artifact_path=content.artifact_path,
                    metadata={"week_start": week_start.isoformat(), "artifact_type": "content"},
                )
                queued_publications += 1

        week_end = week_start + timedelta(days=7)
        quality = repo.quality_summary(week_start.isoformat(), week_end.isoformat())
        dashboard = generate_dashboard(
            settings=settings,
            repo=repo,
            week_start=week_start.isoformat(),
            output_stem=week_start.isoformat(),
        )

        topic_history_memory = repo.get_memory("content_topic_history")
        topic_history = []
        if topic_history_memory is not None:
            topic_history = list(topic_history_memory.get("value", {}).get("topics", []))
        topic_history.extend([c.topic for c in content_results])
        topic_history = topic_history[-50:]
        repo.upsert_memory("content_topic_history", {"topics": topic_history})

        run_summary = {
            "week_start": week_start.isoformat(),
            "week_end_exclusive": week_end.isoformat(),
            "content_count": len(content_results),
            "feedback_count": len(feedback_results),
            "growth_artifact": str(growth_result.artifact_path),
            "community_queue_count": community_result.count,
            "report_path": str(report_result.artifact_path),
            "dashboard_path": str(dashboard.markdown_path),
            "quality_global_avg": quality["global_avg"],
            "queued_publications": queued_publications,
        }
        repo.upsert_memory("last_weekly_run", run_summary)
        repo.finish_run(run_id, status="success", metrics=run_summary)

        print(f"Content created: {len(content_results)}")
        print(f"Growth experiment: {growth_result.artifact_path}")
        print(
            f"Community queue: {community_result.count} drafts -> {community_result.artifact_path}"
        )
        print(f"Feedback memos: {len(feedback_results)}")
        print(f"Weekly report: {report_result.artifact_path}")
        print(f"Dashboard: {dashboard.markdown_path}")
        if args.queue_content_gists:
            print(f"Queued github_gist publications: {queued_publications}")
        return 0
    except Exception as exc:
        repo.finish_run(run_id, status="failed", error_message=str(exc), metrics={})
        raise


def _cmd_build_application_letter(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    _init_environment(settings)
    output_path = Path(args.root).resolve() / args.output
    path = build_public_application_letter(
        settings=settings,
        context=ApplicationLetterInput(
            repository_url=args.repo_url,
            operator_name=args.operator_name,
            operator_location=args.operator_location,
        ),
        output_path=output_path,
    )
    print(f"Application letter generated at: {path}")
    return 0


def _cmd_dashboard(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    result = generate_dashboard(
        settings=settings,
        repo=repo,
        week_start=args.week_start,
        output_stem=args.output_stem,
    )
    print(f"Dashboard markdown: {result.markdown_path}")
    print(f"Dashboard json: {result.json_path}")
    return 0


def _cmd_queue_publish(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    metadata = json.loads(args.metadata_json)
    publication_id = queue_publication(
        repo=repo,
        channel=args.channel,
        title=args.title,
        artifact_path=Path(args.artifact).resolve(),
        metadata=metadata,
    )
    print(f"Queued publication id={publication_id} status=pending_approval channel={args.channel}")
    return 0


def _cmd_list_publish(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    items = repo.list_publications(status=args.status, limit=args.limit)
    if not items:
        print("No publication queue items found.")
        return 0
    print("id | status | channel | title | created_at | external_url")
    print("---|--------|---------|-------|------------|------------")
    for item in items:
        print(
            f"{item.get('id')} | {item.get('status')} | {item.get('channel')} | "
            f"{item.get('title')} | {item.get('created_at')} | {item.get('external_url') or ''}"
        )
    return 0


def _cmd_approve_publish(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    approve_publication(repo=repo, publication_id=args.id, approved_by=args.approved_by)
    print(f"Approved publication id={args.id} by={args.approved_by}")
    return 0


def _cmd_execute_publish(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    result = execute_publication(settings=settings, repo=repo, publication_id=args.id)
    print(
        f"Publication id={result.publication_id} status={result.status} "
        f"external_url={result.external_url or ''}"
    )
    print(f"Note: {result.note}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if args.command == "init":
        return _cmd_init(args)
    if args.command == "run-weekly":
        return _cmd_run_weekly(args)
    if args.command == "build-application-letter":
        return _cmd_build_application_letter(args)
    if args.command == "dashboard":
        return _cmd_dashboard(args)
    if args.command == "queue-publish":
        return _cmd_queue_publish(args)
    if args.command == "list-publish":
        return _cmd_list_publish(args)
    if args.command == "approve-publish":
        return _cmd_approve_publish(args)
    if args.command == "execute-publish":
        return _cmd_execute_publish(args)
    raise ValueError(f"Unhandled command: {args.command}")
