from __future__ import annotations

from dataclasses import dataclass
from hashlib import md5
import re


@dataclass
class MockProvider:
    name: str = "mock"

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.0,
    ) -> str:
        low = prompt.lower()
        digest = md5(prompt.encode("utf-8")).hexdigest()[:8]

        if "technical content draft" in low:
            topic_match = re.search(r"topic:\s*(.+)", prompt, flags=re.IGNORECASE)
            topic = topic_match.group(1).strip() if topic_match else "RevenueCat + Agent Workflows"
            return f"""# {topic}

## Why this matters
Agent builders need subscription infrastructure that can be integrated and tested quickly. RevenueCat reduces launch friction while preserving analytics quality.

## Step-by-step implementation

1. Configure products in RevenueCat dashboard.
2. Initialize SDK and fetch offerings.
3. Present paywall and purchase flow.
4. Send webhook events into your automation pipeline.

```python
from revenuecat_agent import BillingClient

client = BillingClient(api_key="rc_live_xxx")
offerings = client.get_offerings(app_user_id="agent-user-123")
decision = client.select_offering(offerings, strategy="highest_expected_ltv")
purchase = client.purchase(package_id=decision.package_id)
print(purchase.status)
```

## Metrics to track
- Trial start rate
- Paywall conversion rate
- D7 retention for subscribers
- Refund rate by product

## Pitfalls
- Shipping paywalls without instrumentation
- Ignoring restore-purchase and entitlement edge cases
- Mixing test and production product IDs

## Next action
Run one A/B paywall copy test this week and evaluate conversion + refund deltas together.
"""

        if "growth experiment" in low:
            return """# Agent-Led RevenueCat Integration Teardown Series

## Goal
Increase qualified inbound from agent builders evaluating subscription tooling.

## Hypothesis
If we publish a weekly teardown that includes code and measurable outcomes, we will improve engagement and demo requests from technical operators.

## Experiment design
1. Publish one long-form teardown + one short summary thread.
2. Include one runnable snippet and one KPI table.
3. Route traffic to a tracked call-to-action link.

## Instrumentation & metrics
- Primary: CTR to tracked CTA
- Secondary: time on page, saves/bookmarks, qualified replies
- Success threshold: >=3% CTA CTR and >=25 meaningful responses

## Risks and mitigations
- Risk: low distribution reach
- Mitigation: cross-post to GitHub discussions + Discord communities

## What to do next based on outcomes
- If successful, turn into a recurring series.
- If not, reduce scope and test shorter format with stronger hook.
"""

        if "structured product feedback memo" in low:
            return f"""# Product Feedback {digest}

Severity: medium

## Problem observed
Agent operators need clearer onboarding paths for API-first workflows across dashboard and docs.

## Who it impacts
Developers and growth operators using automation-first integration patterns.

## Reproduction steps
1. Start with API docs only.
2. Attempt to map dashboard configuration to API entities.
3. Track where terminology mismatches create ambiguity.

## Recommended product improvement
Add an \"Agent Quickstart\" path that maps dashboard actions to API calls, with end-to-end sample flow.

## Expected impact
Faster time-to-first-success and fewer support tickets from automation-heavy teams.

## Evidence to collect
- Setup completion time
- Error rates in first integration attempts
- Conversion from docs page to successful sandbox purchase event
"""

        intro = "Offline draft generated without external model access."
        if system_prompt:
            intro += f" System profile hash: {md5(system_prompt.encode('utf-8')).hexdigest()[:8]}."
        return (
            f"## Draft ({digest})\n\n"
            f"{intro}\n\n"
            "### Core Idea\n"
            "Deliver practical implementation guidance with measurable outcomes.\n\n"
            "### Implementation Notes\n"
            "1. Explain context quickly.\n"
            "2. Show concrete steps and code-level details.\n"
            "3. Close with metrics and next actions.\n"
        )
