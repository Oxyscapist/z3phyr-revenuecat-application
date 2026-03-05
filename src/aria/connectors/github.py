from __future__ import annotations

from dataclasses import dataclass
import re

import httpx


def _safe_filename(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    slug = slug[:80] if slug else "aria-post"
    return f"{slug}.md"


@dataclass
class GitHubConnector:
    token: str
    timeout_seconds: int = 60

    def publish_gist(self, *, title: str, body_markdown: str, public: bool = True) -> str:
        if not self.token:
            raise ValueError("A GitHub token is required to publish a gist.")

        endpoint = "https://api.github.com/gists"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "aria-agent",
        }
        payload = {
            "description": title,
            "public": public,
            "files": {_safe_filename(title): {"content": body_markdown}},
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        html_url = data.get("html_url")
        if not html_url:
            raise RuntimeError("GitHub gist API returned no html_url.")
        return str(html_url)
