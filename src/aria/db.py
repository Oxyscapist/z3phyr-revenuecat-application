from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import sqlite3
from typing import Any

from aria.utils import utc_now_iso


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS content_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  topic TEXT NOT NULL,
  status TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS growth_experiments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS community_interactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  channel TEXT NOT NULL,
  target TEXT NOT NULL,
  draft_message TEXT NOT NULL,
  status TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS product_feedback (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  title TEXT NOT NULL,
  severity TEXT NOT NULL,
  status TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS weekly_reports (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  week_start TEXT NOT NULL,
  week_end TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  summary_json TEXT NOT NULL
);
"""


@dataclass(frozen=True)
class MetricsSnapshot:
    content_count: int
    experiment_count: int
    interaction_count: int
    feedback_count: int


class Repo:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA_SQL)

    def add_content(
        self,
        title: str,
        topic: str,
        artifact_path: str,
        status: str = "draft",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO content_items(created_at, title, topic, status, artifact_path, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    title,
                    topic,
                    status,
                    artifact_path,
                    json.dumps(metadata or {}),
                ),
            )
            return int(cur.lastrowid)

    def add_growth_experiment(
        self,
        name: str,
        artifact_path: str,
        status: str = "planned",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO growth_experiments(created_at, name, status, artifact_path, metadata_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    name,
                    status,
                    artifact_path,
                    json.dumps(metadata or {}),
                ),
            )
            return int(cur.lastrowid)

    def add_interaction(
        self,
        channel: str,
        target: str,
        draft_message: str,
        status: str = "needs_human_approval",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO community_interactions(created_at, channel, target, draft_message, status, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    channel,
                    target,
                    draft_message,
                    status,
                    json.dumps(metadata or {}),
                ),
            )
            return int(cur.lastrowid)

    def add_feedback(
        self,
        title: str,
        severity: str,
        artifact_path: str,
        status: str = "submitted",
        metadata: dict[str, Any] | None = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO product_feedback(created_at, title, severity, status, artifact_path, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    title,
                    severity,
                    status,
                    artifact_path,
                    json.dumps(metadata or {}),
                ),
            )
            return int(cur.lastrowid)

    def add_weekly_report(
        self, week_start: str, week_end: str, artifact_path: str, summary: dict[str, Any]
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO weekly_reports(created_at, week_start, week_end, artifact_path, summary_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (utc_now_iso(), week_start, week_end, artifact_path, json.dumps(summary)),
            )
            return int(cur.lastrowid)

    def _count_between(self, table: str, week_start: str, week_end: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                f"""
                SELECT COUNT(*) AS c
                FROM {table}
                WHERE created_at >= ? AND created_at < ?
                """,
                (week_start, week_end),
            )
            row = cur.fetchone()
            return int(row["c"])

    def metrics_snapshot(self, week_start: str, week_end_exclusive: str) -> MetricsSnapshot:
        return MetricsSnapshot(
            content_count=self._count_between("content_items", week_start, week_end_exclusive),
            experiment_count=self._count_between(
                "growth_experiments", week_start, week_end_exclusive
            ),
            interaction_count=self._count_between(
                "community_interactions", week_start, week_end_exclusive
            ),
            feedback_count=self._count_between("product_feedback", week_start, week_end_exclusive),
        )

