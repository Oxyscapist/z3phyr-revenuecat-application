from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from aria.config import Settings
from aria.connectors.github import GitHubConnector
from aria.db import Repo
from aria.utils import ensure_dir, write_text


SUPPORTED_CHANNELS = {"github_gist", "x_post"}


@dataclass(frozen=True)
class PublicationResult:
    publication_id: int
    status: str
    external_url: str | None
    note: str


def queue_publication(
    *,
    repo: Repo,
    channel: str,
    title: str,
    artifact_path: Path,
    metadata: dict | None = None,
) -> int:
    if channel not in SUPPORTED_CHANNELS:
        raise ValueError(f"Unsupported channel: {channel}. Supported: {sorted(SUPPORTED_CHANNELS)}")
    if not artifact_path.exists():
        raise FileNotFoundError(f"Artifact not found: {artifact_path}")
    return repo.queue_publication(
        channel=channel,
        title=title.strip(),
        body_path=str(artifact_path),
        metadata=metadata or {},
        status="pending_approval",
    )


def approve_publication(*, repo: Repo, publication_id: int, approved_by: str) -> None:
    repo.approve_publication(publication_id, approved_by=approved_by.strip())


def _manual_x_pack(*, settings: Settings, publication: dict, body_markdown: str) -> str:
    text = body_markdown.strip().splitlines()[0:6]
    summary = "\n".join(text).strip()[:260]
    manual_dir = ensure_dir(settings.artifacts_dir / "publish" / "manual_x")
    manual_path = manual_dir / f"{publication['id']}_x_manual.md"
    write_text(
        manual_path,
        "\n".join(
            [
                "# Manual X Publish Pack",
                "",
                f"- Queue ID: {publication['id']}",
                f"- Title: {publication['title']}",
                f"- Source artifact: {publication['body_path']}",
                "",
                "## Suggested post (trim/edit before posting)",
                "",
                summary,
                "",
                "## Notes",
                "- This workflow is human-approved and manual by design.",
            ]
        )
        + "\n",
    )
    return str(manual_path)


def execute_publication(
    *,
    settings: Settings,
    repo: Repo,
    publication_id: int,
) -> PublicationResult:
    publication = repo.get_publication(publication_id)
    if not publication:
        raise ValueError(f"Publication id {publication_id} not found.")
    if publication["status"] != "approved":
        raise ValueError(
            f"Publication id {publication_id} must be approved before execution. "
            f"Current status={publication['status']}"
        )

    body_path = Path(publication["body_path"])
    if not body_path.exists():
        repo.set_publication_status(
            publication_id,
            status="failed",
            failure_reason=f"Artifact missing: {body_path}",
        )
        return PublicationResult(
            publication_id=publication_id,
            status="failed",
            external_url=None,
            note=f"Artifact missing: {body_path}",
        )

    body = body_path.read_text(encoding="utf-8")
    channel = publication["channel"]

    if channel == "github_gist":
        if not settings.github_token:
            repo.set_publication_status(
                publication_id,
                status="failed",
                failure_reason="ARIA_GITHUB_TOKEN/GITHUB_TOKEN missing.",
            )
            return PublicationResult(
                publication_id=publication_id,
                status="failed",
                external_url=None,
                note="ARIA_GITHUB_TOKEN or GITHUB_TOKEN is required for github_gist publishing.",
            )
        connector = GitHubConnector(token=settings.github_token)
        url = connector.publish_gist(title=publication["title"], body_markdown=body, public=True)
        repo.set_publication_status(publication_id, status="published", external_url=url)
        return PublicationResult(
            publication_id=publication_id,
            status="published",
            external_url=url,
            note="Published to GitHub Gist.",
        )

    if channel == "x_post":
        manual_path = _manual_x_pack(settings=settings, publication=publication, body_markdown=body)
        repo.set_publication_status(
            publication_id,
            status="manual_action_required",
            external_url=manual_path,
        )
        return PublicationResult(
            publication_id=publication_id,
            status="manual_action_required",
            external_url=manual_path,
            note="Generated manual X publish pack.",
        )

    repo.set_publication_status(
        publication_id,
        status="failed",
        failure_reason=f"Unsupported channel: {channel}",
    )
    return PublicationResult(
        publication_id=publication_id,
        status="failed",
        external_url=None,
        note=f"Unsupported channel: {channel}",
    )
