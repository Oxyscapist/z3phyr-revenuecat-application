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

CREATE TABLE IF NOT EXISTS workflow_runs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  started_at TEXT NOT NULL,
  finished_at TEXT,
  command TEXT NOT NULL,
  provider TEXT NOT NULL,
  model TEXT NOT NULL,
  week_start TEXT,
  status TEXT NOT NULL,
  error_message TEXT,
  metrics_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS quality_scores (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  artifact_type TEXT NOT NULL,
  artifact_path TEXT NOT NULL,
  score REAL NOT NULL,
  details_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS publish_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_at TEXT NOT NULL,
  channel TEXT NOT NULL,
  title TEXT NOT NULL,
  body_path TEXT NOT NULL,
  status TEXT NOT NULL,
  approved_by TEXT,
  approved_at TEXT,
  published_at TEXT,
  external_url TEXT,
  failure_reason TEXT,
  metadata_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS memory_store (
  memory_key TEXT PRIMARY KEY,
  value_json TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_registry (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  registered_at TEXT NOT NULL,
  prompt_name TEXT NOT NULL,
  prompt_version TEXT NOT NULL,
  source_path TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_runs_started_at
  ON workflow_runs(started_at);

CREATE INDEX IF NOT EXISTS idx_quality_scores_created_at
  ON quality_scores(created_at);

CREATE INDEX IF NOT EXISTS idx_publish_queue_status_created_at
  ON publish_queue(status, created_at);
"""


@dataclass(frozen=True)
class MetricsSnapshot:
    content_count: int
    experiment_count: int
    interaction_count: int
    feedback_count: int


def _json_loads(value: str | None, default: Any) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


def _row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}


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

    def start_run(
        self,
        *,
        command: str,
        provider: str,
        model: str,
        week_start: str | None = None,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO workflow_runs(
                  started_at, command, provider, model, week_start, status, metrics_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    utc_now_iso(),
                    command,
                    provider,
                    model,
                    week_start,
                    "running",
                    json.dumps({}),
                ),
            )
            return int(cur.lastrowid)

    def finish_run(
        self,
        run_id: int,
        *,
        status: str,
        error_message: str | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE workflow_runs
                SET finished_at = ?, status = ?, error_message = ?, metrics_json = ?
                WHERE id = ?
                """,
                (
                    utc_now_iso(),
                    status,
                    error_message,
                    json.dumps(metrics or {}),
                    run_id,
                ),
            )

    def recent_runs(self, *, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM workflow_runs
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        out: list[dict[str, Any]] = []
        for row in rows:
            item = _row_to_dict(row) or {}
            item["metrics"] = _json_loads(item.pop("metrics_json", "{}"), {})
            out.append(item)
        return out

    def add_quality_score(
        self,
        *,
        artifact_type: str,
        artifact_path: str,
        score: float,
        details: dict[str, Any],
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO quality_scores(created_at, artifact_type, artifact_path, score, details_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (utc_now_iso(), artifact_type, artifact_path, score, json.dumps(details)),
            )
            return int(cur.lastrowid)

    def quality_summary(self, week_start: str, week_end_exclusive: str) -> dict[str, Any]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT artifact_type, COUNT(*) AS c, AVG(score) AS avg_score
                FROM quality_scores
                WHERE created_at >= ? AND created_at < ?
                GROUP BY artifact_type
                ORDER BY artifact_type
                """,
                (week_start, week_end_exclusive),
            ).fetchall()
        by_type = {
            row["artifact_type"]: {
                "count": int(row["c"]),
                "avg_score": round(float(row["avg_score"]), 2) if row["avg_score"] is not None else 0.0,
            }
            for row in rows
        }
        total_count = sum(v["count"] for v in by_type.values())
        if total_count == 0:
            global_avg = 0.0
        else:
            weighted = sum(v["count"] * v["avg_score"] for v in by_type.values())
            global_avg = round(weighted / total_count, 2)
        return {
            "total_count": total_count,
            "global_avg": global_avg,
            "by_type": by_type,
        }

    def queue_publication(
        self,
        *,
        channel: str,
        title: str,
        body_path: str,
        metadata: dict[str, Any] | None = None,
        status: str = "pending_approval",
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO publish_queue(
                  created_at, channel, title, body_path, status, metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (utc_now_iso(), channel, title, body_path, status, json.dumps(metadata or {})),
            )
            return int(cur.lastrowid)

    def list_publications(
        self, *, status: str | None = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM publish_queue
                    WHERE status = ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM publish_queue
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        items: list[dict[str, Any]] = []
        for row in rows:
            item = _row_to_dict(row) or {}
            item["metadata"] = _json_loads(item.pop("metadata_json", "{}"), {})
            items.append(item)
        return items

    def get_publication(self, pub_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM publish_queue
                WHERE id = ?
                """,
                (pub_id,),
            ).fetchone()
        item = _row_to_dict(row)
        if not item:
            return None
        item["metadata"] = _json_loads(item.pop("metadata_json", "{}"), {})
        return item

    def approve_publication(self, pub_id: int, approved_by: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE publish_queue
                SET status = ?, approved_by = ?, approved_at = ?
                WHERE id = ?
                """,
                ("approved", approved_by, utc_now_iso(), pub_id),
            )

    def set_publication_status(
        self,
        pub_id: int,
        *,
        status: str,
        external_url: str | None = None,
        failure_reason: str | None = None,
    ) -> None:
        published_at = utc_now_iso() if status == "published" else None
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE publish_queue
                SET status = ?,
                    external_url = COALESCE(?, external_url),
                    published_at = COALESCE(?, published_at),
                    failure_reason = COALESCE(?, failure_reason)
                WHERE id = ?
                """,
                (status, external_url, published_at, failure_reason, pub_id),
            )

    def publication_status_counts(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT status, COUNT(*) AS c
                FROM publish_queue
                GROUP BY status
                """
            ).fetchall()
        return {row["status"]: int(row["c"]) for row in rows}

    def upsert_memory(self, memory_key: str, value: dict[str, Any]) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO memory_store(memory_key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(memory_key)
                DO UPDATE SET value_json = excluded.value_json, updated_at = excluded.updated_at
                """,
                (memory_key, json.dumps(value), utc_now_iso()),
            )

    def get_memory(self, memory_key: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT memory_key, value_json, updated_at
                FROM memory_store
                WHERE memory_key = ?
                """,
                (memory_key,),
            ).fetchone()
        if row is None:
            return None
        return {
            "memory_key": row["memory_key"],
            "value": _json_loads(row["value_json"], {}),
            "updated_at": row["updated_at"],
        }

    def list_memory(self, *, prefix: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            if prefix:
                rows = conn.execute(
                    """
                    SELECT memory_key, value_json, updated_at
                    FROM memory_store
                    WHERE memory_key LIKE ?
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (f"{prefix}%", limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT memory_key, value_json, updated_at
                    FROM memory_store
                    ORDER BY updated_at DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        return [
            {
                "memory_key": row["memory_key"],
                "value": _json_loads(row["value_json"], {}),
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]

    def register_prompt(self, prompt_name: str, prompt_version: str, source_path: str) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO prompt_registry(registered_at, prompt_name, prompt_version, source_path)
                VALUES (?, ?, ?, ?)
                """,
                (utc_now_iso(), prompt_name, prompt_version, source_path),
            )
            return int(cur.lastrowid)

    def list_prompt_registry(self, *, limit: int = 100) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM prompt_registry
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [(_row_to_dict(row) or {}) for row in rows]

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
