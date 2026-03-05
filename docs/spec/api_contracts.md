# API Contracts

## Public endpoints
- GET /health
- POST /work-items
- GET /work-items/{id}
- PATCH /work-items/{id}
- DELETE /work-items/{id}

## Error responses
- 400 validation error
- 401/403 authentication/authorization error
- 404 missing resource
- 429 rate limit reached
- 5xx transient server or dependency failure

## Rate limiting
- Per-user and per-IP limits
- Stricter limits for expensive routes
