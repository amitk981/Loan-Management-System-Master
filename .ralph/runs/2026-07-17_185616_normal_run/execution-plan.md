# Execution Plan

Selected slice: 009E4-source-bank-rationale-and-approval-evidence-closure

## Outcome

Close the source-bank governance audit gap through the existing public
`activate_source_bank_account` / `resolve_source_bank_account` module interface. Accepted first
activations and replacements will retain a bounded safe rationale and immutable request, author,
role/team, network, version, predecessor/successor, and audit facts without claiming that the
provisioner independently approved the change.

## TDD Behaviours

1. RED then GREEN: public activation and replacement retain distinct reviewable rationales and
   exact author/request/network history, while `VersionHistory` has no false approver or approval
   reference and protected evidence contains no bank plaintext, ciphertext, capability, or unrelated
   identity.
2. RED then GREEN: blank, over-500-character, control-character, bank-number, and protected-token
   rationales are rejected before governance/version/audit writes.
3. RED then GREEN: one-field mutations of rationale, digest, request, author/role/team/network,
   effective history, or false approval attribution make current resolution fail closed.
4. Preserve the production catalogue proof and twice-run PostgreSQL five-caller first/replacement
   race contract, adding winner rationale/attribution assertions without weakening clean-loser
   guarantees.

## Implementation

- Add one migration-owned protected rationale/attribution manifest to the source-bank governance
  row, leaving unrecoverable legacy rows honestly unresolved rather than fabricating a reason.
- Centralise safe-rationale validation and canonical activation/replacement evidence construction
  inside the existing deep governance module.
- Write author truth only to author/actor fields; leave reviewer/approver/approval-reference fields
  empty unless a future governed approval owner supplies them.
- Reconcile canonical row, version, audit, effective-range, and predecessor/successor evidence in
  `resolve_source_bank_account`.

## Verification and Evidence

- Save focused failing and passing Django test output under `evidence/terminal-logs/` using the
  orchestrator venv interpreter.
- Run focused configuration/disbursement tests, Django check, migration sync, and applicable
  frontend build/typecheck/lint/tests; leave the complete backend coverage suite to the orchestrator.
- Save sanitized activation/replacement manifests and the no-default-grant proof. Attempt the
  declared PostgreSQL races twice if the sandbox socket is available; otherwise retain the exact
  local collection/skip evidence for the orchestrator-owned capability gate.
- Complete changed-files, risk, review, final summary, handoff, progress/state, slice status, and
  sharpen the next one or two Not Started slices only when the already-open Epic 009 source/digest
  supplies concrete improvements.
