# Execution Plan

Selected slice: `008J-blank-dated-cheque-and-cancelled-cheque-custody`

## Scope and seams

- Extend the existing `security_instruments` owner with one protected blank-dated cheque per
  retained security package, its immutable evidence/history, and database constraints that keep
  invocation, presentation, return, and amount facts null for later slices.
- Extend the immutable `processes.security_instrument_evidence` contract with canonical
  application-owned bank/cancelled-cheque and same-application scan selectors. Public HTTP and
  reveal calls cross this coordinator; executable security code will not import applications,
  members, legal documents, approvals, or central sensitive-access policy.
- Reuse `shared.encryption.FieldEncryption`, the central masker/reveal policy, the retained package
  lock and scope checks, and `security_instruments.modules.evidence_recorder`.
- Add only the source-defined POST/GET/PATCH and explicit reveal action. Do not add custody-event,
  download, invocation, return, checklist-completion, readiness, loan-account, or frontend behavior.

## TDD tracer cycles

1. Add a public HTTP create/read tracer proving Compliance can collect the sanctioned borrower's
   six-digit cheque only against the exact retained active bank and verified cancelled cheque;
   ordinary responses/evidence are masked and the database value is encrypted. Save the failing
   RED output before adding production code, then save GREEN output.
2. Add public PATCH tests for exact replay, changed preparation, distinct Company Secretary held
   custody, immutable preparer/custodian evidence, field/date/status/custody constraints, and
   forbidden later-lifecycle fields; implement the minimal locked transition module.
3. Add canonical evidence matrices for missing/pending/conflicting/cross-member bank and cancelled
   cheque facts plus nullable same-application scan provenance and atomic checklist projection.
4. Add permission/object-scope/read-only matrices, fixed masking, explicit central reveal with
   reason/no-store/success-and-denial audit, duplicate hash protection, tamper/missing-key behavior,
   and executable dependency guards.
5. Add PostgreSQL five-worker create and changed-custody races, asserting one material winner, one
   terminal custodian, exact winning request/actor/workflow linkage, and zero loser success evidence.

## Verification and handoff

- Run scoped tests after each RED/GREEN cycle with the mandated Ralph virtualenv interpreter.
- Run Django check, migration sync, full backend coverage, and all frontend lint/typecheck/test/build
  gates; run the declared PostgreSQL race contract twice when the configured database is available.
- Save API examples and terminal logs under the run evidence folder; write changed-files, risk,
  review, and final-summary artifacts; update API contracts, assumptions if needed, progress, state,
  handoff, this slice status, and sharpen the next one or two Not Started slices using already-opened
  Epic 008 source material.
