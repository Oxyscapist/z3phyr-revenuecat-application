# Data Flow & Storage

## Entities
- User
- Work Item
- AuditEvent

## Data flow
1. Client sends request to API
2. API authenticates and validates payload
3. Service layer writes work-item and audit event
4. Read path serves from DB with optional caching

## Storage
- Primary relational DB for transactional data
- Object storage for user uploads (if applicable)

## Cost/scale notes
- TTL-based caches for hot paths
- Archive low-value historical events periodically
