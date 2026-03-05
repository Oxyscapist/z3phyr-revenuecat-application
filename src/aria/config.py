from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class Settings:
    agent_name: str
    tone: str
    positioning: str
    provider: str
    model: str
    timezone: str
    gemini_api_key: str | None
    openai_api_key: str | None
    openai_base_url: str
    github_token: str | None
    x_bearer_token: str | None
    approval_mode: str
    data_dir: Path
    artifacts_dir: Path
    prompts_dir: Path
    db_path: Path

    @classmethod
    def from_env(cls, root: Path) -> "Settings":
        data_dir = Path(os.environ.get("ARIA_DATA_DIR", root / "data")).resolve()
        artifacts_dir = Path(
            os.environ.get("ARIA_ARTIFACTS_DIR", root / "artifacts")
        ).resolve()
        prompts_dir = Path(
            os.environ.get("ARIA_PROMPTS_DIR", root / "prompts")
        ).resolve()
        return cls(
            agent_name=os.environ.get("ARIA_AGENT_NAME", "ARIA"),
            tone=os.environ.get("ARIA_TONE", "Professional and warm"),
            positioning=os.environ.get(
                "ARIA_POSITIONING",
                "Autonomous Revenue Intelligence Agent with a friendly disposition",
            ),
            provider=os.environ.get("ARIA_PROVIDER", "gemini").strip().lower(),
            model=os.environ.get("ARIA_MODEL", "gemini-2.5-flash-lite"),
            timezone=os.environ.get("ARIA_TIMEZONE", "UTC"),
            gemini_api_key=os.environ.get("GEMINI_API_KEY"),
            openai_api_key=os.environ.get("OPENAI_API_KEY"),
            openai_base_url=os.environ.get(
                "OPENAI_BASE_URL", "https://api.openai.com/v1"
            ),
            github_token=os.environ.get("ARIA_GITHUB_TOKEN", os.environ.get("GITHUB_TOKEN")),
            x_bearer_token=os.environ.get("ARIA_X_BEARER_TOKEN"),
            approval_mode=os.environ.get("ARIA_APPROVAL_MODE", "human").strip().lower(),
            data_dir=data_dir,
            artifacts_dir=artifacts_dir,
            prompts_dir=prompts_dir,
            db_path=Path(os.environ.get("ARIA_DB_PATH", data_dir / "aria.db")),
        )

