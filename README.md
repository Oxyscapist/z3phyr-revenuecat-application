# z3phyr

`z3phyr` is an autonomous agent scaffold optimized for RevenueCat's **Agentic AI Developer & Growth Advocate** application and role requirements.

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
- Persistence: SQLite (`data/z3phyr.db`)
- Outputs: markdown artifacts in `artifacts/`

## Quickstart

```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .
```

Initialize:

```bash
python -m z3phyr init
```

Run one weekly cycle offline (proof mode):

```bash
python -m z3phyr run-weekly --provider mock --week-start 2026-03-02
```

Run one weekly cycle with Gemini:

```bash
set GEMINI_API_KEY=your_key_here
set Z3PHYR_PROVIDER=gemini
set Z3PHYR_MODEL=gemini-2.5-flash-lite
python -m z3phyr run-weekly --week-start 2026-03-02
```

Generate public application letter:

```bash
python -m z3phyr build-application-letter --repo-url https://github.com/<user>/<repo>
```

## Environment variables

- `Z3PHYR_AGENT_NAME` (default: `z3phyr`)
- `Z3PHYR_TONE` (default: `Professional and warm`)
- `Z3PHYR_POSITIONING` (default: `Helpful assistant with friendly disposition`)
- `Z3PHYR_PROVIDER` (`gemini` | `openai` | `mock`)
- `Z3PHYR_MODEL` (default: `gemini-2.5-flash-lite`)
- `GEMINI_API_KEY`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL` (optional for compatible APIs)
- `Z3PHYR_DATA_DIR` (default: `data`)
- `Z3PHYR_ARTIFACTS_DIR` (default: `artifacts`)

## Repository map

- `src/z3phyr/cli.py`: command entrypoints
- `src/z3phyr/llm/`: provider abstraction and implementations
- `src/z3phyr/workflows/`: content, growth, community, feedback, reporting, application-letter workflows
- `docs/`: requirement mapping, application assets, plans
- `docs/spec/`: generated product spec set
- `artifacts/`: execution outputs (created at runtime)

## Submission support docs

- `docs/01_requirement_matrix.md`
- `docs/02_public_application_letter.md`
- `docs/03_application_form_answers_template.md`
- `docs/04_build_plan.md`
- `docs/05_submission_checklist.md`
