# Execution Plan

Selected slice: 009H2-advice-authority-current-truth-and-delivery-closure

## Scope

Correct only the existing disbursement-advice workflow and its retained evidence. Keep
`DisbursementWorkflow.send_advice` as the small public interface and keep email transport behind the
existing Manual/Fake adapter seam. Consume the stable pending communication created by 009G2; do
not add a second advice workflow or any frontend surface.

## Behaviours and TDD order

1. Add one public-interface role/scope test, capture RED, then correct catalogue grants and canonical
   Senior Manager Finance/Credit Manager object scope while denying CFC-only and synthetic scope.
2. Add one public send/replay test, capture RED, then bind the pending communication to current
   canonical recipient, approved/effective template and variables, rendered subject/body, transfer,
   register, provider, sender, action, audit, and workflow truth.
3. Add one rollback/fresh-adapter test, capture RED, then make provider idempotency durable through a
   stable communication/delivery key and canonical payload; provider rejection must leave pending
   truth only.
4. Add focused drift tests one at a time for recipient, template/rendered payload, provider facts,
   upstream evidence, and ledgers; each must conflict without new delivery or evidence.
5. Add or update the PostgreSQL five-caller race contract and retain collection/delegation evidence
   for the orchestrator's twice-run authoritative gate.

## Verification and evidence

- Run every backend command with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
- Save focused RED/GREEN logs, role matrix, rollback/retry trace, architecture-probe results, safe
  audit manifest, Django check, migration-sync check, and PostgreSQL collection/delegation evidence
  under this run's `evidence/` directory.
- Run impacted backend tests only, plus Django check and migration sync. Do not run the complete
  backend suite or coverage; the orchestrator owns those gates.
- Run frontend build, typecheck, lint, and tests only if shared contracts or frontend files are
  affected; otherwise record the backend-only rationale.

## Closeout

Update the API contract, epic digest if implementation truth changes, selected slice status, Ralph
state/progress/handoff, changed-files, risk assessment, review packet, and final summary. Recheck and
sharpen the next one or two Not Started slices using only already-open source material. Do not commit,
stage, push, or modify protected/source files.
