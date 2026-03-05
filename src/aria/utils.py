from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
import re


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
    return normalized or "untitled"


def write_text(path: Path, body: str) -> Path:
    ensure_dir(path.parent)
    path.write_text(body, encoding="utf-8")
    return path


def monday_for_week(week_start: str | None = None) -> date:
    if week_start:
        return date.fromisoformat(week_start)
    today = date.today()
    return today - timedelta(days=today.weekday())

