# Database Rules

## Current Codebase
A minimal Django backend scaffold exists for health checks. No persistent database schema, models, or migrations have been introduced yet.

## Source Direction
Source docs recommend PostgreSQL with a Django modular-monolith backend and service-layer business logic.

## Safety Rules
- Never drop tables automatically.
- Never drop columns automatically.
- Never rename columns without migration strategy and rollback notes.
- Never change financial, audit, or identity semantics without an ADR.
- Every migration must include tests and rollback notes.
- Demo/mock data must not be treated as production truth.
- Database-impacting slices are at least Medium risk.

## Future Setup Needed
When backend code is introduced, update this file with migration commands, seed commands, test database setup, naming conventions, multi-tenant rules, soft-delete rules, and audit trail conventions.
