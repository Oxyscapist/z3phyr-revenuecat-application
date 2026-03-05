# Architecture

## High-level diagram
- Client (CLI + GitHub) -> API service -> Primary database
- Worker/queue for long-running operations and retries

## Core modules/layers
- UI layer
- API layer
- Domain/services layer
- Data access layer
- Observability layer

## Scalability notes
- Stateless API instances for horizontal scaling
- Queue-based processing for heavy jobs
- Cache frequent reads and expensive upstream calls
