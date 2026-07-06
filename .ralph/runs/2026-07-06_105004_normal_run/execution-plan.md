# Execution Plan

Selected slice: `003I-notification-adapter-shell`

## Scope
- Add the backend `Communication` persistence shell in the existing `sfpcl_credit.communications` app.
- Expose `POST /api/v1/communications/send/` and `GET /api/v1/communications/`.
- Render message snapshots from approved/effective `ContentTemplate` rows without sending real messages or calling providers.
- Audit communication snapshot creation with metadata only.
- Update working API contracts, assumptions/digest as needed, and Ralph run artifacts.

## TDD Plan
1. Add an API integration test proving an authorized send renders subject/body snapshots, persists a pending `Communication`, writes one metadata-only audit row, and list returns the row through standard pagination.
2. Run that focused test red and save the failure in `evidence/terminal-logs/communications-red.log`.
3. Implement the model, migration, service functions, URL/view wiring, and narrow permission catalogue entries.
4. Add/extend focused tests for validation, unknown query parameters, UUID checks, inactive/unapproved templates, merge variables, and `401`/`403` no-write behavior.
5. Run the focused tests green and save output in `evidence/terminal-logs/communications-green.log`.

## Implementation Notes
- Use existing `ContentTemplate` schema; do not alter it unless tests prove a contract mismatch.
- Use `communications.communication.read` and `communications.communication.send` as narrow source-aligned permissions; record the catalogue assumption.
- Treat extra `merge_data` keys as validation errors for deterministic snapshot rendering.
- Keep `delivery_status` at `pending`; `sent_at` and `external_message_id` remain null because this slice performs no real delivery.
- Do not include full rendered message bodies in audit metadata.

## Gates and Evidence
- Run backend check, backend tests, migrations check, backend coverage with the required venv interpreter.
- Run frontend tests/typecheck/lint/build because Ralph gates require them, even though this slice is backend-only.
- Save API response examples for send, list, `401`, `403`, and validation failure under run evidence.
- Save changed-files, risk assessment, review packet, final summary, state/progress/handoff/slice updates.
