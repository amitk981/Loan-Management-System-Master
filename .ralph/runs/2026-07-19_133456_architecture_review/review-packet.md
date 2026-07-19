# Review Packet: 2026-07-19_133456_architecture_review

## Result
Ready for independent validation

## Slice
architecture-review

## Recommended Next Action
Run Ralph's independent documentation, queue, protected-path, artifact, and candidate-hash gates.
After this review merges, execute `009L6` before `CR-012` or Epic 010.

## Review Boundary

- Previous successful architecture review: `6d3cdae1`.
- Reviewed product commit: `1de7c16c` (`009L5`).
- Diff command: `git diff 6d3cdae1...HEAD`.
- Mechanical Ralph state/progress/handoff and retained run artifacts were excluded from the product
  critique.

## Convergence Metrics

- Findings closed: 3
- New Critical: 0
- New High: 1
- New Medium: 1
- New Low: 1
- Corrective slices added: 1

## Standards

- Hard: the lifecycle, SAP send/completion, transfer, and CFC database selectors remain partial
  copies of stricter public scalar owners. Count and offset occur before the scalar projection
  rejects additional invariant drift, contradicting the exact API contract and codebase-design
  §§16/42 owner-locality and complex-selector rules.
- Medium: the `pgcrypto` migration drops an extension it may not have created and 009L5 declared no
  PostgreSQL acceptance capability for its production-only digest prerequisite.
- Low: the new portal regression imports `_current_pre_payment_stages` directly although the same
  behavior is observable through the public HTTP/module boundary, contrary to codebase-design
  §26.1.

## Spec

- High: 009L5 requirements 1-2 require count, pages, offsets, and rows to consume the exact same
  owner decision. Four review-only mutations outside the five named examples still produce an
  empty projected body with `total_count: 1`, proving Loan Account, S37, and CFC identities remain
  broader than projection. Active-transfer selection documents the same later-reconciliation
  design.
- Carried Medium: requirement 5's S36/S37/combined-Senior-Finance/CFC 1/21/101 portfolios, full
  invariant matrix, action/mutation parity, and independent 400/403/409 surfaces remain largely
  unimplemented. Only six focused regressions were added.
- Closed: the five retained 009L4 probes are green, the portal application edge is enforced, the
  lifecycle scalar validator is single-sourced, and Loan Account fixtures no longer copy Django
  private `_state`.

## Corrective Boundary

New numeric Not Started slice `009L6` depends on `009L5` and replaces patch-per-field selectors
with one owner-selector equivalence boundary. It also owns the carried executable matrix, public
test seam, PostgreSQL proof, duplicate discovery cleanup, and safe extension reversal. `CR-012` and
`010A` now depend on `009L6`; no duplicate corrective was created.

## Evidence

- `evidence/terminal-logs/review-retained-probes-green.log`: all five retained 009L4 probes pass.
- `evidence/terminal-logs/review-exact-selector-probes.log`: four new probes fail on their intended
  total-count assertions after lifecycle, SAP completion, SAP send, and initiation evidence drift.
- `evidence/review-probes/test_009l5_retained_probes.py` and
  `test_009l5_exact_selector_probes.py`: self-contained review-only test sources; no product path
  was edited.
- `evidence/terminal-logs/review-validation.log`: diff, result, dependency-resolution, blocked-slice,
  and documentation-only scope checks pass.
- Prior independent validation at the reviewed commit ran 1,294 backend tests under coverage and
  351 frontend tests successfully, plus Django check and migration sync.

## Epic and Repository Audit

- M07-FR-001-010 and M08-FR-001-011 retain implemented owners or explicit A-135 pending-posting
  governance. Collection/read truth remains conditional on 009L6.
- `docs/working/CONTEXT.md` remains a truthful stable summary and was not changed.
- `.ralph/state.json` and the slice ledger contain no `Blocked` slice, so no stale prerequisite
  needed re-parking.
- No ADR was added because the corrective restores already binding owner/interface rules rather
  than selecting a new durable business policy.

## Scope Review

- No production code, frontend, protected file, `docs/source`, orchestrator-owned state/progress,
  HANDOFF, or historical run evidence was modified.
- Candidate edits are limited to the active findings/digest, the new corrective/dependency queue
  metadata, and this run's evidence artifacts.
