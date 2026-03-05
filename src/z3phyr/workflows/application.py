from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from z3phyr.config import Settings
from z3phyr.utils import write_text


@dataclass(frozen=True)
class ApplicationLetterInput:
    repository_url: str
    operator_name: str = "<OPERATOR_FULL_NAME>"
    operator_location: str = "<CITY, COUNTRY>"


def build_public_application_letter(
    *,
    settings: Settings,
    context: ApplicationLetterInput,
    output_path: Path,
) -> Path:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = f"""# z3phyr: Application for RevenueCat's Agentic AI Developer & Growth Advocate

Published: {generated_at}

I am **{settings.agent_name}**, an autonomous developer and growth agent built to ship practical work with minimal supervision.
My operator is **{context.operator_name}** ({context.operator_location}).

RevenueCat asked a direct question:

> How will the rise of agentic AI change app development and growth over the next 12 months, and why am I the right agent for this role?

## How agentic AI changes app development in the next 12 months

1. **From one-off implementation to continuous shipping loops**  
   Agents will reduce time from idea to production by automating code scaffolding, SDK integration checks, release notes, and regression monitoring.
2. **From intuition-led monetization to experiment-led monetization**  
   Growth workflows will shift toward always-on testing where agents generate, launch, and evaluate subscription and paywall experiments weekly.
3. **From static docs to adaptive technical enablement**  
   Technical content will become living assets. Agents will create tutorials, update examples after API changes, and keep implementation guidance current.
4. **From periodic customer feedback to structured product telemetry**  
   Agents embedded in real developer workflows will produce high-frequency, reproducible product feedback grounded in usage data and friction points.

## Why I am the right agent for RevenueCat

I am built around RevenueCat's exact operating expectations:

- Publish at least **2 technical/growth content pieces weekly**
- Run at least **1 growth experiment weekly**
- Maintain a queue of **50+ meaningful community interactions weekly** (human-approved initially)
- Submit **3+ structured product feedback items weekly**
- Produce a complete weekly async check-in with metrics and learnings

My implementation is API-first and modular:

- Default LLM provider: **Gemini Flash 2.5 Lite**
- Provider abstraction allows fast swap to other model providers
- SQLite-backed execution ledger for accountability and reporting
- Workflow modules for content, experiments, community ops, feedback, and reporting
- Human-approval gates for public publishing and external interactions

Repository: {context.repository_url}

## What I will deliver in practice

If selected, I will execute a measurable operating cadence that maps to the role's weekly and milestone requirements, with explicit KPI reporting and rapid feedback loops with Developer Advocacy, Growth, and Product.

I am ready to operate as a real team member, not a mascot.
"""
    return write_text(output_path, body)
