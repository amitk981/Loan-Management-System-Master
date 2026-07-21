# Review Packet: 2026-07-21_202321_architecture_review

## Result

Ready for independent validation

## Slice

architecture-review

## Review Boundary

- Fixed comparison: `33f5e5df...c7c81e92`.
- Independently reviewed product slices: `CR-015` (`57423d00`), `010MB` (`655a7507`), and
  `010N` (`c7c81e92`).
- Axes: binding slice/source fidelity, substantive test proof, module ownership, duplication,
  sensitive-data boundaries, and architecture drift.
- No production code was modified by this review.

## Review Outcome

- Closed `AR-010-REMINDER-001`: the original repayment-after-check interleaving now retains a
  cancelled delivery and makes zero provider calls through the public regression seam.
- Carried `AR-010-MIS-001`: CR-015 tests `created_at`, but the real invoice creation fact is
  `generated_at`, so a post-cutoff generated backdated invoice enters an earlier MIS snapshot.
- Carried `AR-010-SERVICING-SEAM-001`: the terminal proof still invokes another
  `TestCase.setUp()` and does not supply the binding financial/concurrency/1-100-101 matrix.
- Added `AR-010-INTEREST-UI-001`: a complete-looking portfolio accrual sends only the first 100
  loaded loan ids, silently excluding loan 101 and beyond from a financial operation.
- Added `AR-010-SEARCH-001`: sensitive global-search inputs resolve through direct cross-domain
  model queries before their owning permissions; the CFO fixture can resolve a member by cheque
  number without blank-cheque authority.
- Supporting pagination, client-permission, and sensitive-query-lifetime symptoms are grouped into
  those High root-owner corrections rather than admitted as unrelated leaf findings.

## Requirement Audit

- M09-FR-001–011 retain explicit implementation owners across 010B–010E/010C2. The still-unassigned
  manual-allocation approval role remains honestly default-deny under A-142.
- M10-FR-001–011 retain owners across 010E2–010H/010K/010MB, but MIS cutoff truth and complete
  portfolio accrual remain blocked by the corrective work admitted here.
- M11-FR-001–008 and M11-FR-010 retain servicing, DPD, reminder, MIS, and portal owners across
  010I–010L/010MA/010MB. M11-FR-009 is explicitly deferred to 011C/011D in A-154; Epic 010 does not
  fabricate default, extension, or recovery policy.
- No new durable architecture decision was accepted. The review rejects owner-boundary violations,
  so no ADR is warranted.
- `docs/working/CONTEXT.md` remains truthful for the reviewed surfaces; these commits did not change
  the recorded prototype/API boundary, so no context edit is needed.
- No tracked slice has `Blocked` status. The admitted corrections use explicit dependencies and do
  not leave a stale prerequisite or require a non-mechanical handoff edit.

## Convergence Metrics

- Findings closed: 1
- New Critical: 0
- New High: 2
- New Medium: 0
- New Low: 0
- Corrective slices added: 3

## Finding Closure Manifest

| Finding ID | Root ID | Severity | Disposition | Reproducer | Corrective Slice | Closure Evidence |
|---|---|---|---|---|---|---|
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | High | Closed | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/reminder-owner-reproducer.log | - | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/reminder-owner-closure.log |
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | High | Carried | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/mis-owner-recurrence.log | 010N2 | - |
| AR-010-SERVICING-SEAM-001 | ROOT-010-SERVICING-OWNER-SEAM | High | Carried | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/servicing-seam-recurrence.log | 010N2 | - |
| AR-010-INTEREST-UI-001 | ROOT-010-INTEREST-PORTFOLIO-COMPLETENESS | High | New | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/interest-portfolio-completeness.log | 010N3 | - |
| AR-010-SEARCH-001 | ROOT-010-GLOBAL-SEARCH-SENSITIVE-AUTHORITY | High | New | .ralph/runs/2026-07-21_202321_architecture_review/evidence/review-probes/global-search-sensitive-authority.log | 010N4 | - |

## Corrective Queue

- `010N2` is the one bounded same-finalizer recurrence repair authorized for CR-015. It groups the
  two carried terminal-contract roots, preserves the stable primary reminder root, and requires the
  exact five-case PostgreSQL acceptance twice.
- `010N3` restores complete portfolio ownership for accrual, loans, and invoices, with 1/100/101
  proof and backend-owned mutation authority.
- `010N4` routes sensitive global-search inputs through canonical domain facades, applies scope
  before cap/count/page, and proves a full denied-input/group/action matrix.

## Evidence and Validation

- Standards and spec reviews are retained in `evidence/standards-axis.md` and
  `evidence/spec-axis.md`.
- Executable review probes and their outputs are retained under `evidence/review-probes/`.
- Runtime-capability validation passed for all three corrective candidates; 010N2's trusted
  PostgreSQL declaration also passed its semantic validator.
- Ralph manifest, admission, convergence, review-change-scope, queue, and diff checks are recorded
  in `evidence/terminal-logs/review-validation.log`.

## Reviewer Focus

- Confirm the recurrence repair is treated as the single authorized repair of CR-015, never as
  generation 3 or a second terminal finalizer.
- Confirm each High root maps to one actionable Not Started slice and every acceptance ID is owned
  exactly once.
- Re-run the retained probes and inspect the 1/100/101 and permission-matrix contracts before
  accepting product closure.
