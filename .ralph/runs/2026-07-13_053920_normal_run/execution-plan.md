# Execution Plan

Selected slice: 007A3-approval-matrix-maker-checker-governance

## Scope and contract

- Replace rule/committee create and supersede writes with immutable pending proposals carrying a
  mandatory reason and maker/request metadata.
- Add proposal detail plus explicit approve/reject transition endpoints. Only a distinct, active
  user with persisted `cfo` or `company_secretary` approval authority may decide a proposal.
- Activate or supersede the proposed effective-dated configuration only during approval while the
  shared configuration lock is held; revalidate retained-history overlap and committee authority.
- Expose status/version and resource-level available actions, stable validation/forbidden/conflict
  errors, and idempotent terminal reads without altering existing approval-case snapshots.
- Preserve the existing list/resolver projections for active and retained historical rows. No
  frontend change is in this governance-only backend/API slice.

## TDD tracer bullets

1. RED: public API creation must require reason and return pending without changing resolver,
   VersionHistory, or activation audit. GREEN: proposal persistence and serialization.
2. RED: self/ordinary/inactive/wrong-authority decisions are denied with zero writes; distinct
   CFO/CS approval activates exactly once. GREEN: authority and transition boundary.
3. RED: rejection requires reason, leaves effective configuration untouched, and terminal/stale
   transitions return stable errors. GREEN: reject/version/idempotency handling.
4. RED: supersede approval and approval-time overlap/committee-authority revalidation are atomic;
   loser snapshots remain unchanged. GREEN: locked activation and coherent history/audit evidence.
5. RED: open ApprovalCase snapshots remain unchanged and detail available-actions match executable
   authority. GREEN: projection/action parity and regression proof.

## Implementation and verification

- Add at most one approvals migration for the proposal model and its constraints/indexes.
- Update the approval configuration deep module, thin views/URLs, API contract documentation, and
  epic digest. Record any source-silent transition detail in ASSUMPTIONS.md.
- Save each focused RED/GREEN command under `evidence/terminal-logs/`, then run backend check,
  migration sync, full coverage, and all frontend build/typecheck/lint/test gates.
- Save changed-files, risk assessment, review packet, final summary, state/progress/handoff, mark
  only 007A3 Complete, and inspect/sharpen the next two Not Started slices from already-open sources.
