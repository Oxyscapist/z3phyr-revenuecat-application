# MVP Backlog

## Priority 1
- Authentication and basic user profile
- Create and view work-items
- Input validation and error handling
- Basic analytics/telemetry events

## Priority 2
- Edit and delete work-items
- Search/filter/sort for work-items
- Rate limiting and abuse guardrails

## Priority 3
- Admin dashboard for ops visibility
- Export/share capability
- Experiments and feature flags

## Acceptance criteria
- Users can create and read work-items with authorization checks enforced server-side
- Critical API routes return documented status codes and validation errors
- Core journey is covered by at least one deterministic end-to-end smoke test
- Operational alerts exist for 5xx spikes and dependency failures
