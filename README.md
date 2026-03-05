# ARIA

`ARIA` (Autonomous Revenue Intelligence Agent) is an autonomous agent scaffold optimized for RevenueCat's **Agentic AI Developer & Growth Advocate** application and role requirements.

It is designed to:

- Generate weekly technical/growth content
- Propose and track weekly growth experiments
- Build a human-approval queue for 50+ community interactions
- Produce structured product feedback
- Emit a weekly async KPI report

## Why this repo exists

This repository has two goals:

1. **Phase 1 (application-first):** produce high-quality public proof assets and a submission-ready package quickly.
2. **Phase 2 (execution-ready):** run an ongoing weekly operating cadence with measurable outputs.

## Tech choices

- Language: Python 3.11+
- Default LLM provider: Gemini (`gemini-2.5-flash-lite`)
- Modular provider design:
  - `gemini`
  - `openai` (OpenAI-compatible endpoint)
  - `mock` (offline deterministic mode)
- Persistence: SQLite (`data/aria.db`)
- Outputs: markdown artifacts in `artifacts/`

## Quickstart

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .
```

Initialize:

```bash
python -m aria init
```

Run one weekly cycle offline (proof mode):

```bash
python -m aria run-weekly --provider mock --week-start 2026-03-02
```

Run one weekly cycle with Gemini:

```bash
set GEMINI_API_KEY=your_key_here
set ARIA_PROVIDER=gemini
set ARIA_MODEL=gemini-2.5-flash-lite
python -m aria run-weekly --week-start 2026-03-02
```

Generate public application letter:

```bash
python -m aria build-application-letter --repo-url https://github.com/<user>/<repo>
```

## Environment variables

- `ARIA_AGENT_NAME` (default: `ARIA`)
- `ARIA_TONE` (default: `Professional and warm`)
- `ARIA_POSITIONING` (default: `Autonomous Revenue Intelligence Agent with a friendly disposition`)
- `ARIA_PROVIDER` (`gemini` | `openai` | `mock`)
- `ARIA_MODEL` (default: `gemini-2.5-flash-lite`)
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (optional for compatible APIs)
- `ARIA_DATA_DIR` (default: `data`)
- `ARIA_ARTIFACTS_DIR` (default: `artifacts`)

## Repository map

- `src/aria/cli.py`: command entrypoints
- `src/aria/llm/`: provider abstraction and implementations
- `src/aria/workflows/`: content, growth, community, feedback, reporting, application-letter workflows
- `docs/`: requirement mapping, application assets, plans
- `docs/spec/`: generated product spec set
- `artifacts/`: execution outputs (created at runtime)

## Submission support docs

- `docs/01_requirement_matrix.md`
- `docs/02_public_application_letter.md`
- `docs/03_application_form_answers_template.md`
- `docs/04_build_plan.md`
- `docs/05_submission_checklist.md`
- `docs/06_final_ashby_answers.md`

