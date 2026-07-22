# Execution Plan

Selected slice: 011C-extension-note-workflow

## Scope and seams

- Keep all eligibility, date, replay, document-scope, transition, cure, and expiry rules behind the existing `DefaultWorkflow` interface; the HTTP view remains a thin adapter.
- Add one database-owned `ExtensionNote` per `DefaultCase`, linked to the existing governed `LoanDocument` for the same loan application, with bounded states and immutable active dates.
- Add only the declared grant endpoint and scheduler-facing workflow methods. Do not add staff UI, a Non-Payment Note, new document infrastructure, or an unstated approval route.

## TDD sequence

1. RED/GREEN: prove the public grant endpoint creates one active, exactly one-year Extension Note for an eligible unpaid non-intentional case, links the exact loan-file document, and emits audit/workflow evidence.
2. RED/GREEN: add input, authority, eligibility, stale-assessment, date, payment/closure, and foreign/missing-document rejection behavior.
3. RED/GREEN: prove exact replay returns the existing note, changed replay and a second extension conflict, and the database constraint converges concurrent PostgreSQL grants.
4. RED/GREEN: prove payment during extension cures the case without deleting/mutating the note and expiry processing is retry-safe, marks review required, and creates no Non-Payment Note.
5. Add migration and permission seed, route/view adapter, response serialization, and default-case detail/action projection as each behavior demands.

## Validation and evidence

- Save every focused RED and GREEN command/output under `evidence/terminal-logs/` using `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Run focused defaults/API/document/permission tests, the exact two-test PostgreSQL acceptance label when locally available, Django check, and migration consistency. Do not run the complete backend suite or coverage lane.
- Inspect migration/model sync, targeted diff/stat, and protected paths; then complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md` with source-to-test traceability.

## Decision-policy constraint

The sources make extension approval conditional but define no extension-specific approval configuration or approval endpoint. The implementation will activate directly when no configured route exists and will not invent one; any configuration-dependent approval mechanism that cannot be expressed through an existing authoritative seam will be recorded as an explicit open assumption rather than fabricated.
