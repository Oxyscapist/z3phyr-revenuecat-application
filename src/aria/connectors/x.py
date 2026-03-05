from __future__ import annotations

from dataclasses import dataclass


@dataclass
class XConnector:
    bearer_token: str | None = None

    def publish_post(self, text: str) -> str:
        # X posting is intentionally manual-first for this system.
        # We keep this connector explicit so automated posting can be added safely later.
        raise NotImplementedError(
            "Automated X posting is disabled. Use ARIA human-approval manual publish flow."
        )
