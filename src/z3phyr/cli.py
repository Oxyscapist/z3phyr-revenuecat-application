from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path
import sys

from z3phyr.config import Settings
from z3phyr.db import Repo
from z3phyr.llm.factory import build_provider
from z3phyr.utils import ensure_dir, monday_for_week
from z3phyr.workflows.application import (
    ApplicationLetterInput,
    build_public_application_letter,
)
from z3phyr.workflows.community import build_interaction_queue
from z3phyr.workflows.content import generate_content_batch
from z3phyr.workflows.feedback import generate_feedback_batch
from z3phyr.workflows.growth import generate_growth_experiment
from z3phyr.workflows.reporting import generate_weekly_report


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="z3phyr",
        description="z3phyr autonomous developer and growth advocate agent",
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

    return parser.parse_args(argv)


def _settings(root: str) -> Settings:
    return Settings.from_env(Path(root).resolve())


def _init_environment(settings: Settings) -> Repo:
    ensure_dir(settings.data_dir)
    ensure_dir(settings.artifacts_dir)
    repo = Repo(settings.db_path)
    return repo


def _cmd_init(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    print("Initialized z3phyr environment")
    print(f"data_dir={settings.data_dir}")
    print(f"artifacts_dir={settings.artifacts_dir}")
    print(f"db_path={repo.db_path}")
    return 0


def _cmd_run_weekly(args: argparse.Namespace) -> int:
    settings = _settings(args.root)
    repo = _init_environment(settings)
    provider = build_provider(settings, force_provider=args.provider)
    week_start = monday_for_week(args.week_start)

    print(f"Running weekly cycle for {week_start.isoformat()} with provider={provider.name}")

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

    print(f"Content created: {len(content_results)}")
    print(f"Growth experiment: {growth_result.artifact_path}")
    print(f"Community queue: {community_result.count} drafts -> {community_result.artifact_path}")
    print(f"Feedback memos: {len(feedback_results)}")
    print(f"Weekly report: {report_result.artifact_path}")
    return 0


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


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv or sys.argv[1:])
    if args.command == "init":
        return _cmd_init(args)
    if args.command == "run-weekly":
        return _cmd_run_weekly(args)
    if args.command == "build-application-letter":
        return _cmd_build_application_letter(args)
    raise ValueError(f"Unhandled command: {args.command}")
