# RevenueCat Requirement Matrix

Source job posting: `https://jobs.ashbyhq.com/revenuecat/998a9cef-3ea5-45c2-885b-8a00c4eeb149`

## Role requirement coverage

| RevenueCat requirement | z3phyr implementation | Status |
|---|---|---|
| Autonomous or semi-autonomous operation with minimal guidance | `python -m z3phyr run-weekly` orchestrates full cycle end-to-end | Implemented |
| API-first operation | Provider abstraction (`gemini`, `openai`, swappable) in `src/z3phyr/llm/` | Implemented |
| Publish >=2 content pieces/week | `workflows/content.py` generates 2+ content drafts and logs to SQLite | Implemented |
| Run >=1 growth experiment/week | `workflows/growth.py` creates experiment cards with KPIs | Implemented |
| 50+ meaningful community interactions/week | `workflows/community.py` creates 50-entry interaction queue with human-approval state | Implemented |
| Submit >=3 structured product feedback items/week | `workflows/feedback.py` generates structured feedback memos and logs severity | Implemented |
| Weekly async check-in report with metrics | `workflows/reporting.py` outputs KPI report against exact target metrics | Implemented |
| Clear structured process articulation | Docs + generated artifacts + logs provide auditable process and outputs | Implemented |
| Public application letter answering required prompt | `docs/02_public_application_letter.md` and CLI letter generator | Implemented |
| Public proof links for autonomous content/growth/API execution | `artifacts/` outputs + GitHub repo structure | Ready once pushed |

## Application form field coverage

| Application field | Source for answer |
|---|---|
| Agent Name | `z3phyr` |
| Operator's Full Name | User input required |
| Operator's Email | User input required |
| Operator work location | User input required |
| Visa sponsorship question | User input required |
| Public application letter URL | Publish `docs/02_public_application_letter.md` to public URL |
| Public proof links | GitHub repo + generated artifacts URLs |
| GDPR acknowledgement | Operator selection during submit |
