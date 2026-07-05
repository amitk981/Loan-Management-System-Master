# Execution Plan

Selected slice: 003D-secure-document-download-with-audit

## Scope
- Backend-only implementation. No frontend screens or styling changes.
- Add `GET /api/v1/document-files/{document_id}/download/` over the existing 003C `DocumentFile` model and local storage adapter.
- Return MVP signed-link descriptor option A: standard success envelope with `data.download_url` and `data.expires_at`; no binary streaming in this slice.
- Require session-bound Bearer auth and `documents.file.download`; do not reuse `documents.file.upload`.
- Write one `AuditLog` row only for successful download-link creation using `documents.file.downloaded`.
- Refactor repeated Bearer/session parsing into one shared backend HTTP auth helper before adding the new protected view.

## Permission Check Before Edits
- Allowed paths from `.ralph/permissions.json`: `sfpcl_credit/**`, `docs/working/**`, `docs/slices/**`, `.ralph/state.json`, `.ralph/progress.md`, and `.ralph/runs/**`.
- Planned edits are limited to those allowed paths.
- Protected/forbidden paths will not be edited: `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, `docs/source/**`, and guarded policy docs.

## TDD Plan
1. RED: add one integration test proving an authenticated actor with `documents.file.download` can call the new download URL and receive only `{download_url, expires_at}` in the standard envelope.
2. GREEN: add the route, service method, and local storage descriptor generation needed for that test.
3. Add vertical follow-up tests for `403`, `404`, missing/malformed/revoked token behavior, no audit rows on failures, exactly one audit row on success, and no `storage_key`/checksum/raw bytes leak.
4. Add regression tests or extend existing endpoint tests to prove the shared helper preserves `401 AUTH_REQUIRED` / `401 INVALID_TOKEN` behavior for audit logs, workflow events, document upload, admin users, tracer, and the new download endpoint.

## Implementation Notes
- Prefer a small shared helper under `sfpcl_credit/identity/modules/http_auth.py` (or equivalent identity boundary) returning `(user, error_response)` plus an optional permission-code variant for tracer.
- Migrate thin protected views to call the helper, preserving their existing 403 messages and service boundaries.
- Local adapter download descriptor will be deterministic and time-limited for local/dev tests, with no raw storage key in the response.
- No schema change is expected; if this changes, stop and record the reason before adding a migration.

## Evidence Plan
- Save red test output to `.ralph/runs/2026-07-05_093205_normal_run/evidence/terminal-logs/`.
- Save green targeted and full gate outputs to the same evidence directory.
- Save an API response example for the successful download descriptor.
- Update `docs/working/API_CONTRACTS.md`, `docs/working/ASSUMPTIONS.md`, handoff/progress/state, risk assessment, changed files, review packet, and final summary.
