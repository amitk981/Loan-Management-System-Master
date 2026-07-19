# Execution Plan

Selected slice: 009L5-epic-009-exact-selector-and-consumer-parity-closure

## Boundary

- Change only Epic 009 selector/consumer correctness and its retained tests/evidence.
- Preserve lifecycle, SAP completion, readiness, initiation, transfer, and action authority behind
  their current public owner modules; do not add Epic 010 behavior or posting-confirmation authority.
- No visual redesign or hosted browser work; CR-012 remains the browser-evidence owner.

## Public behaviors to prove

1. Loan Account, S36, S37, Senior Finance, and CFC collections compute totals, offsets, pages, and
   rows from one exact eligible identity decision per branch. Evidence drift never changes an empty
   projection into a non-zero count or strands later rows, including runs longer than four.
2. Exact collections retain stable ordering and bounded query work for 1, 21, and 101 mixed rows,
   including first, middle, last, and out-of-range pages.
3. Every SAP completion consumer binds member, application, and customer-code evidence to the same
   current owner decision; another application's completion cannot advance portal or readiness.
4. Lifecycle single-row and bulk reads use one evidence validator, eliminating duplicated scalar
   decisions while retaining their public interfaces.
5. Action visibility and mutations agree for the same actor/row, denied identities are not
   disclosed, and 400/403/409 response surfaces remain independent.

## RED -> GREEN tracer bullets

1. Retain the five architecture-review probes as product regressions and run them RED; implement
   exact selector/count parity and the portal application-edge check; rerun GREEN.
2. Add one focused regression at a time for longer drift runs and mixed page boundaries, using
   public factories/module interfaces instead of copying Django private `_state`; make each GREEN
   through the owning selector interface.
3. Add focused reverse-consumer and action/transport/error parity cases only where the retained
   suite lacks an executable assertion; make each GREEN without caller-side policy duplication.

## Verification and evidence

- Save focused RED and GREEN command output under `evidence/terminal-logs/` using the mandated
  Ralph Python interpreter.
- Run impacted backend labels only (not the complete suite), Django check, migration-sync check,
  and any impacted frontend test/typecheck/build gates if a frontend consumer changes.
- Inspect targeted diffs and query ceilings, then complete `risk-assessment.md`, `review-packet.md`,
  and `final-summary.md`; leave state, slice status, changed-files, commit, merge, and push to Ralph.
