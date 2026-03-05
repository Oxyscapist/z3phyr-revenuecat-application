# Phase 2 Hardening (Implemented)

This document summarizes the production-hardening layer added after the application package.

## Added capabilities

1. Prompt registry and versioning
- Prompt files live in `prompts/` as JSON.
- Every workflow run registers prompt name/version/source into `prompt_registry`.

2. Quality scoring rubric
- Scoring engine in `src/aria/quality.py`.
- Scores are persisted in `quality_scores`.
- Weekly report includes quality summary.

3. Run history and memory
- `workflow_runs` tracks command lifecycle, status, and metrics.
- `memory_store` keeps rolling memory (e.g. `last_weekly_run`, `content_topic_history`).

4. Human-approval publishing pipeline
- Queue content for publishing: `queue-publish`.
- Approve publication: `approve-publish`.
- Execute approved publication: `execute-publish`.
- GitHub Gist publishing is supported.
- X publishing is manual-first via generated publish pack.

5. Observability dashboard
- Command: `python -m aria dashboard`.
- Output: `artifacts/dashboard/latest.md` and `artifacts/dashboard/latest.json`.

6. Scheduling
- GitHub Actions workflow: `.github/workflows/aria-weekly.yml`.
- Supports weekly schedule + manual dispatch.

## Key commands

```bash
python -m aria run-weekly --provider mock --week-start 2026-03-02 --queue-content-gists
python -m aria list-publish --status pending_approval
python -m aria approve-publish --id 1 --approved-by "Sankalp Sunder"
python -m aria execute-publish --id 1
python -m aria dashboard --week-start 2026-03-02 --output-stem latest
```

## Required env vars for live publishing

- `ARIA_GITHUB_TOKEN` (or `GITHUB_TOKEN`) for `github_gist`.
- `GEMINI_API_KEY` for live Gemini runs.
