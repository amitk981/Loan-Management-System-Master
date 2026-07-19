# Review Packet: 2026-07-19_093632_architecture_review

## Result
Complete

## Slice
architecture-review

## Review Boundary

- Previous successful architecture-review commit: `4e44116d`.
- Product commit reviewed: `de3d0f0c` (`009L`), using `4e44116d..de3d0f0c`.
- Later `staging` commits are Ralph infrastructure/queue maintenance and were excluded from the
  product review boundary.
- Epic boundary audited: Epic 009 M07/M08 to Epic 010.

## Standards

The independent Standards pass reported five findings, worst severity High:

1. **High:** Loan Account 360 counts and database-slices a broad role-qualified queryset before
   object scope and immutable-evidence projection. Totals and page reachability can disclose denied
   or incoherent rows and strand later eligible accounts.
2. **High:** S36 candidate selection is narrowed to intake creator/receiver even though the public
   SAP create owner accepts another authorised Credit Manager. Action reachability does not match
   mutation reachability.
3. **Medium:** Loan Account 360 replaced the established tab shell with a new facts-grid/lock-card
   composition. Removing mock data was correct; replacing the approved layout violates the
   frontend hard rules.
4. **Medium:** Staff workspace and SAP composition remain unbounded/N+1 before final Python
   pagination, while query ceilings are demonstrated with only one row.
5. **Medium:** Browser/component tests do not click or submit the newly declared actions, leaving
   transport and error-state behavior unproved.

## Spec

The independent Spec pass reported five findings, worst severity High:

1. **High:** CFC workspace actions use effective role alone, while the mutation additionally
   requires the governed CFC approval-authority type and Critical permission.
2. **High:** retained browser evidence intercepts auth/workspace/Loan Account APIs and mutates local
   fixtures; it does not execute the declared real S36-S41 workflows.
3. **High:** the initial-loan-payment ledger accepts `posted` using only a reference/timestamp,
   despite A-135 withholding the actor, permission, adapter, and immutable acceptance evidence.
4. **Medium:** database-bounded eligible pagination is not implemented; workspace rows are composed
   before Python slicing and Loan Account rows are sliced before coherence projection.
5. **Medium:** required drift/action matrices and MP14 opposite-order selection remain incomplete;
   the retained race assertion does not prove exactly one initial posting row.

These are reported separately rather than merged; related symptoms are grouped into corrective work
by canonical owner below.

## Verification

- Focused backend: 43 tests passed, with two PostgreSQL-only skips.
- Focused frontend: 19 tests across five files passed.
- Three review-only probes failed on intended assertions: S36 mutation/action mismatch, CFC
  mutation/action mismatch, and member/account SAP evidence disagreement.
- Static inspection confirmed scope/count/slice ordering, evidence-free `posted` acceptance, mocked
  browser routes, and three byte-identical screenshots among the retained evidence set.
- Queue lint and `009L3` runtime-capability validation passed.
- The complete backend suite and full coverage were not repeated; the orchestrator retains the
  authoritative 009L gates and independently validates this documentation-only candidate.

## Findings and Corrective Work

- Closed: the missing M07-FR-009 capability now has an atomic pending obligation; the separate
  false-terminal-state defect remains open in `009L3`.
- Closed: Loan Account 360 no longer combines a real account with another borrower's mock servicing
  data; the separate layout-fidelity defect remains open in `009L3`.
- Added `009L3`, a numeric Not Started slice depending on 009L, for public-owner authority parity,
  canonical SAP completion evidence, scope-first bounded pagination, pending-only posting truth,
  safe prototype layout, and omitted negative/race/MP14 matrices.
- Mapped the real-browser evidence finding to existing Not Started `CR-012`, now ordered after
  `009L3`; no duplicate corrective was created.
- No root-cause-boundary escalation is warranted: this review closed two findings and added one
  grouped corrective. The previous review also did not have additions exceed closures.

## Convergence Metrics

- Findings closed: 2
- New Critical: 0
- New High: 4
- New Medium: 2
- New Low: 0
- Corrective slices added: 1
- Existing corrective slice: CR-012

## Repository Health

- `CONTEXT.md` remains truthful.
- Epic 009 M07/M08 requirements have retained owners or explicit A-135 pending governance, subject
  to the open findings.
- No slice is `Blocked`; no stale prerequisite required re-parking.
- No ADR is required because both correctives restore binding contracts rather than establish a
  new architecture.
- Candidate scope is documentation, queue metadata, and current-run evidence only.

## Recommended Next Action
Run `009L3` before `CR-012`, then admit Epic 010 only after both correctives pass their trusted
PostgreSQL and real-browser contracts.

Review skill summary: Standards found 5 issues (worst High: scope/pagination and S36 owner drift);
Spec found 5 issues (worst High: CFC authority, false SAP completion, and mocked browser proof).
