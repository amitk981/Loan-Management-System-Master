# Execution Plan

Selected slice: `009G2-post-disbursement-register-checklist-and-replay-closure`

## Scope and invariants

- Extend only the existing public disbursement-success and post-disbursement checklist paths.
- Keep transfer success atomic across the transfer, funded loan activation, durable Loan Register
  evidence, stable pending borrower-advice identity, audit, and workflow facts.
- Preserve provider delivery as pending; do not add repayment, schedule, interest, default, closure,
  or borrower-notification success behavior.
- Preserve the source dependency direction by exposing a narrow immutable post-transfer decision
  from a top-level/coordinator seam for the legal checklist owner.
- Require active Senior Manager Finance authority, the explicit checklist-signature permission,
  and Stage-5 object scope. Fail closed on missing, duplicate, cross-object, or stale evidence.
- Return API §45.2's replay wrapper with the exact retained original §31.4 response and no writes.

## TDD sequence

1. Add one public transfer-success test for the exact §31.4 response, Loan Register evidence,
   stable pending advice identity, and absence of sent/checklist/servicing side effects. Run it RED
   and save the output.
2. Add replay and evidence-drift assertions one behavior at a time; implement the minimum model,
   migration, selector, and workflow changes needed for each GREEN result.
3. Add public §27.7 checklist tests for the valid signer and immutable evidence binding, then the
   governed multi-role, inactive, permission-only, role-only, cross-object, pre-success, exact
   replay, changed replay, and stale-evidence cases.
4. Add/extend PostgreSQL five-caller transfer and checklist race tests for one complete winner and
   clean losers; collect locally when the declared runtime is available and otherwise leave the
   authoritative twice-run execution to the orchestrator.

## Verification and handoff

- Run focused affected backend test modules with
  `/Users/amitkallapa/LMS/.ralph/venv/bin/python`, plus Django check and migration sync.
- Run impacted frontend tests only if frontend code is touched, then frontend typecheck, lint, and
  build as required by the run contract. Do not run the complete backend suite or coverage locally;
  the orchestrator owns that authoritative gate.
- Update the API contract ledger and Epic 009 digest with the retained public response/evidence
  shape, then sharpen the next one or two Not Started slices only if current source extracts reveal
  missing concrete requirements.
- Save red/green and gate evidence, changed-files, risk assessment, review packet, final summary,
  state, progress, handoff, and the selected slice status. Do not add, commit, or push.
