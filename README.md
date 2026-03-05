# ARIA

`ARIA` (Autonomous Revenue Intelligence Agent) is an autonomous agent scaffold optimized for RevenueCat's **Agentic AI Developer & Growth Advocate** application and role requirements.

It is designed to:

- Generate weekly technical/growth content
- Propose and track weekly growth experiments
- Build a human-approval queue for 50+ community interactions
- Produce structured product feedback
- Emit a weekly async KPI report
- Maintain a human-approval publication queue (GitHub Gist + X manual packs)
- Track quality scores, run history, prompt versions, and memory state

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

Run with publication queue drafts:

```bash
python -m aria run-weekly --provider mock --week-start 2026-03-02 --queue-content-gists
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

Generate observability dashboard:

```bash
python -m aria dashboard --week-start 2026-03-02 --output-stem latest
```

Queue + approve + execute publication:

```bash
python -m aria queue-publish --channel github_gist --artifact artifacts/content/2026-03-02_01_example.md --title "ARIA Content: Example"
python -m aria list-publish --status pending_approval
python -m aria approve-publish --id 1 --approved-by "Sankalp Sunder"
python -m aria execute-publish --id 1
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
- `ARIA_GITHUB_TOKEN` or `GITHUB_TOKEN` (required for `github_gist` execution)
- `ARIA_X_BEARER_TOKEN` (reserved for future X automation)
- `ARIA_APPROVAL_MODE` (default: `human`)
- `ARIA_DATA_DIR` (default: `data`)
- `ARIA_ARTIFACTS_DIR` (default: `artifacts`)
- `ARIA_PROMPTS_DIR` (default: `prompts`)

## Repository map

- `src/aria/cli.py`: command entrypoints
- `src/aria/llm/`: provider abstraction and implementations
- `src/aria/workflows/`: content, growth, community, feedback, reporting, application-letter workflows
- `src/aria/workflows/publishing.py`: queue/approval/execution publish workflow
- `src/aria/workflows/dashboard.py`: observability dashboard generation
- `src/aria/prompts.py`: prompt registry loading + template rendering
- `src/aria/quality.py`: artifact quality scoring
- `prompts/`: versioned prompt definitions
- `.github/workflows/aria-weekly.yml`: scheduled weekly pipeline
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
- `docs/07_phase2_hardening.md`

