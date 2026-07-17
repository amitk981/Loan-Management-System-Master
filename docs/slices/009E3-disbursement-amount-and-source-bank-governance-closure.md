# Slice 009E3: Disbursement Amount and Source-Bank Governance Closure

## Status
Not Started

## Parent Epic
Epic 009: SAP, Loan Account Creation, and Disbursement

## Depends On
- 009E2

## Runtime Capabilities

postgresql-five-race-acceptance

## Goal

Permit the source-defined positive lesser disbursement amount within the sanctioned facility and
make source-bank activation one complete, historically versioned, race-safe configuration decision.

## Source / Review References

- `docs/source/screen-spec.md` S38-S39
- `docs/source/integrations.md` §§9.1-9.5
- `docs/source/codebase-design.md` §§6.5, 16.3-16.4, 22, 26, 38, and 42
- `docs/source/auth-permissions.md` §§15.6, 26.5, 30.2, and 31.2
- `docs/source/data-model.md` §§19.3, 29-30, and 34
- `docs/working/REVIEW_FINDINGS.md` entry for `2026-07-17_105635_architecture_review`

## Concrete Requirements

1. Accept an initiation amount when it is positive, fits the 18,2 boundary, does not exceed the
   immutable loan-terms amount or sanctioned amount, and the account remains entirely unfunded.
   S39 makes the amount editable within sanction limits; CFC authorisation remains the independent
   approval of that exact frozen lesser amount. Continue to reject zero, negative, over-terms,
   over-sanction, changed-replay, already-funded, or incoherent account amounts.
2. Prove the complete public success path consumes a loan account created through
   `loans.modules.loan_account_lifecycle`, not a direct `LoanAccount`/`LoanTerms` insertion. Freeze
   and reconcile the loan creation/status-history/audit/workflow identities needed to distinguish
   an owner-created sanctioned account from raw equivalent-looking rows.
3. Make an active `SourceBankAccountGovernance` row structurally impossible without its complete
   activation version and `config.changed` audit. Reorder the atomic writer around a pre-generated
   governance identity or otherwise satisfy the database invariant without a transient incomplete
   active row. Add `config.source_bank_account.activate` to the canonical permission catalogue as
   Critical while assigning it to no role; governance can then grant the declared authority without
   tests inventing a permission absent from production. Keep the source account encrypted/redacted
   and retain all prior rows.
4. On replacement, append an explicit deactivation/version transition for the old decision, close
   its effective range, and retain its original activation evidence. The new decision must identify
   the exact predecessor. Current resolution must reject missing, overlapping, duplicate, changed,
   cross-linked, or temporally incoherent activation/deactivation histories.
5. Serialize first activation and replacement across different bank accounts. Convert the partial
   unique constraint's concurrent loser into the stable domain conflict with no orphan governance,
   version, audit, or permission evidence.
6. Replace the `inspect.getsource`/`__all__`/`hasattr` implementation-shape assertions with public
   `DisbursementWorkflow` behavior and executable dependency-boundary assertions. Preserve 009E2's
   typed readiness decision, exact §45.2 replay, stable errors, redaction, and zero later-state
   effects.

## Test Cases

- Publicly initiate exact sanctioned and two positive lesser amounts; reject boundary/overage and
  changed replay while asserting the exact frozen amount across row/audit/workflow/task.
- Run the genuine documentation/SAP/readiness/bank path with a loan produced by the public loan
  lifecycle. Raw account/terms rows or changed creation/history evidence fail with zero writes.
- Attempt active governance without either proof relation and assert database rejection. Replace an
  active account and assert exact activation/deactivation versions, audits, effective ranges, and
  predecessor linkage; mutate each relation one field at a time and resolution fails closed.
- Seed the canonical catalogue and assert the activation permission exists at Critical risk with no
  default role grant; an ordinary seeded role remains denied.
- Twice run five concurrent first-activation and replacement attempts on PostgreSQL. Each run keeps
  one complete current winner, historical predecessor truth, stable loser conflicts, and no orphan
  evidence.

## Evidence Required

Failing-first copies of the architecture probes; amount boundary matrix; source-bank lifecycle
manifest; genuine loan-owner initiation trace; twice-run PostgreSQL races; focused tests, Django
check, migration sync, and full configured gates.

## Risk Level
High

## Acceptance Criteria

- A valid positive lesser amount within the facility can reach CFC review without weakening any
  readiness, account, bank, replay, or sanction guard.
- No active or replaced source-bank decision exists without one complete, temporally coherent,
  immutable configuration history.
- Tests cross the same public owner seams as production callers and race losers leave no artifacts.

## Done Checklist
- [ ] Execution plan written
- [ ] Tests written or updated
- [ ] Code implemented
- [ ] API contracts updated, if needed
- [ ] Database rules followed, if needed
- [ ] Permissions tested
- [ ] Audit events tested
- [ ] Tests/typecheck/lint/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated
- [ ] State updated
- [ ] Commit delegated to the orchestrator only after passing configured gates
