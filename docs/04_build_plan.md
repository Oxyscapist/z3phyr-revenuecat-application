# Build Plan: Application First, Immediate Phase 2

## Objective

Submit a high-quality RevenueCat application today, then transition immediately into a production-ready execution agent.

## Phase 1 (Now -> submission in next few hours)

1. Finalize role requirement coverage and proof architecture.
2. Generate and polish the public application letter.
3. Build and run the weekly execution pipeline in offline proof mode.
4. Produce evidence artifacts (content, growth, community queue, feedback, weekly report).
5. Prepare application form answer sheet with all URLs.
6. Publish on GitHub and submit Ashby application.

## Phase 2 (Immediately after submission)

1. Configure live Gemini provider and secure key management.
2. Add GitHub and X connectors with human-approval publish gates.
3. Add prompt/version registry and experiment memory.
4. Add quality scoring rubric for content and feedback outputs.
5. Add observability dashboard (run status, KPIs, failure reasons).
6. Add scheduled execution (cron/GitHub Actions) with weekly check-in auto-generation.

## Acceptance criteria

- Application contains:
  - public letter URL
  - verifiable proof links
  - clear autonomous operating model
- Agent can run a full weekly cycle and generate:
  - >=2 content drafts
  - >=1 growth experiment
  - >=50 interaction queue entries
  - >=3 feedback memos
  - 1 weekly KPI report

## Immediate commands

```bash
pip install -e .
python -m z3phyr init
python -m z3phyr run-weekly --provider mock --week-start 2026-03-02
python -m z3phyr build-application-letter --repo-url https://github.com/<user>/<repo>
```
