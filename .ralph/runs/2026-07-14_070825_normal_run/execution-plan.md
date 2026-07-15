# Execution Plan

Selected slice: 007R-legacy-approval-history-and-frozen-identity-closure

## Public interfaces and invariants

- Keep the existing approval-case list/detail/action and Credit Sanction Register endpoints.
- Treat the exact pre-007O `approval-review-v2` package as historically readable only when its
  original immutable provenance and review facts validate. Unknown schemas and malformed current
  packages remain nondisclosing.
- Emit `approval-review-v3` for newly routed packages and require its complete frozen member,
  application-reference, and sanction-term facts for approve/reject/register writes.
- Leave return-for-clarification available to an assigned legacy-cycle actor, while approve and
  reject return a clear terminal-facts blocker with zero writes. The existing correction,
  independent review, and new-cycle interfaces perform remediation without modifying cycle one.
- Resolve formal approver display identity only from routed immutable names or a newly persisted
  action-time display name. Preserve user ids; legacy missing names serialize as null.
- Serialize legacy register JSON defensively as null/empty values without live reconstruction.

## TDD tracer bullets

1. RED/GREEN: persist the exact pre-007O v2 package and prove actor-scoped detail/history remains
   readable while approve/reject are blocked without writes and return remains enabled.
2. RED/GREEN: drive return -> appraisal correction -> independent review -> new cycle, proving the
   first cycle is byte-for-byte unchanged and the new package is v3/terminal-complete.
3. RED/GREEN: persist approved/rejected legacy register rows with empty frozen JSON and prove
   actor-scoped list serialization is null-safe and never reconstructs current owner facts.
4. RED/GREEN: rename routed/action actors before terminal generation and prove register authority,
   action rows, names, ids, and times retain immutable route/action-time identities.
5. Add malformed v3, permission/scope, count/pagination, optimistic-version, and zero-write
   regressions needed to preserve the existing security and race contracts.

## Implementation and verification

- Add one nullable immutable action display-name field and one migration; do not backfill it from
  mutable users.
- Split historical-package validation from terminal-package validation inside the deep approval
  module, update the credit-owned projector to v3, and remove live user-name reads from authority
  serialization.
- Make register serialization null-safe and update the maintained API contract/digest only for the
  delivered schema/remediation/null semantics.
- Save focused RED/GREEN logs under `evidence/terminal-logs/`, then run Django check, migration
  sync, the focused backend suite, full backend coverage, and all configured frontend gates.
- Perform separate standards and spec reviews, record changed files/risk/review/final evidence,
  sharpen the next one or two Not Started slices using already-opened sources, then update Ralph
  progress/state/handoff and mark only 007R Complete.
