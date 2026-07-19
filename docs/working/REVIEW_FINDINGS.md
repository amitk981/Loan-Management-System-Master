# Active Review Findings

This is the bounded, active architecture-review ledger. Reviews prepend new entries here and keep
only unresolved findings or the most recent closure evidence. The complete historical ledger
through 2026-07-18 is retained unchanged at
`docs/working/archive/REVIEW_FINDINGS-through-2026-07-18.md` and in Git history.

## Review admission and convergence

- Critical/High correctness, security, financial/data-integrity, or binding source-contract
  findings create immediate corrective slices.
- Medium findings are grouped into the owning slice or epic closure. Low findings remain recorded
  unless they naturally combine with higher-severity work.
- Related symptoms are grouped by root owner rather than creating one corrective slice per symptom.
- Every `review-packet.md` reports non-negative integer counts for findings closed, new findings by
  severity, and corrective slices added. Validation checks the reported additions against the
  candidate queue diff.
- Two consecutive reviews with no new Critical/High findings expand routine cadence from four to
  eight completed slices. Any new Critical/High resets cadence to four. Epic boundaries always
  trigger a review.

## Open findings from 2026-07-19_104332_architecture_review

Reviewed product commit: `547c6835` (009L3), relative to successful architecture-review commit
`eacf85e3`. Commit `692589f5` only retains candidate-hash proof; `755525c2` is Ralph infrastructure
and is outside the completed product-slice review. Epic 009's M07/M08 boundary was re-audited because
009L3 is its product corrective closure.

### 009L4 — Epic 009 canonical read and bounded pagination closure

- **High — SAP consumers still choose different completion records:** requirement 3 says member,
  account, readiness, workspace, and Loan Account reads must use one canonical completion decision
  and reject duplicate/newer-stale/cross-application evidence identically. The member facade selects
  the newest member request in `sap_customer_profile.py:305-350`, while the account facade still
  independently selects an application/customer-code-specific request in lines 353-393. A retained
  review probe adds a newer incoherent cross-application completion: the canonical member decision
  returns unavailable, but the account decision accepts the older completion. This can let Loan
  Account/readiness consumers trust SAP truth rejected by the SAP member owner, contradicting
  M07-FR-010 and the slice's binding disbursement gate.
- **Medium — truthful pages still require unbounded duplicated evidence work:** 009L3 fixed the
  previous count/leakage defect, but `loan_account_360.list_accounts` now materializes and deeply
  projects every eligible account before Python slicing (`loan_account_360.py:46-60`). Its database
  filter repeats a partial copy of lifecycle/transfer invariants owned elsewhere, and the staff
  workspace calls the full scan for every nominal 100-row page (`disbursement_workspace.py:62-74`)
  before slicing again. Work therefore grows with the full portfolio and can approach repeated
  full scans, contrary to requirements 4/7 and codebase-design §§16/42. The one-row ceilings cannot
  prove the required 1/21/101 behavior.
- **Medium — the declared executable closure remains partial:** the diff adds one S36 allow case,
  one CFC governed-authority denial, one SAP digest drift, and pending-posting assertions, but not
  the full role/permission/task/maker-checker/current-evidence action matrix, independent SAP
  component/consumer matrix, 21/101-row mixed-scope pagination, exact create/send/complete/transfer
  transport/error matrix, or MP14 opposite-order unit case required by 009L3. The new browser case
  proves opposite-order selection with fulfilled routes; `CR-012` correctly remains the separate
  owner of the nine-state real-Django browser workflow.
- **Low — acceptance tests overstate or duplicate their observable scope:** the exact PostgreSQL
  label is an empty subclass of an already discovered race class, so the full suite discovers the
  same two races twice instead of replacing the prior surface as codebase-design §26.2 directs. The
  browser test named “every governed tab” opens only Loan Ledger and checks that two other buttons
  exist; the remaining unavailable tab bodies are not exercised.

New corrective `009L4` groups these symptoms at the SAP/read-selector/workspace root and is ordered
after 009L3, before existing `CR-012`, and before Epic 010. `CR-012` continues to own only the real-
Django screenshot/evidence contract; no duplicate browser corrective was added.

## Closed in this review

- **Scope-first pagination correctness:** denied or immutable-evidence-incoherent Loan Accounts are
  now excluded before totals and Python page slicing, so they no longer leak counts or strand later
  valid rows. `009L4` owns the distinct bounded-query and selector-locality remainder.
- **Pending-only initial SAP posting:** model and database constraints now reject `posted`, current
  transfer evidence requires one pending obligation, and both retained five-way PostgreSQL races
  assert its singular status. A-135 remains explicit; no unsupported SAP success is fabricated.
- **Loan Account 360 layout fidelity:** the approved eleven-tab shell is restored with existing
  `Tabs`; Epic 010 bodies remain explicitly unavailable without mock servicing facts or new styling.

The S36 all-Credit-Manager reachability and governed CFC admission probes also pass, but canonical
SAP/action-matrix closure remains grouped under 009L4 rather than counting those symptoms as a
separate closed root finding.

## Review evidence

- Independent 009L3 validation retained a green complete backend coverage run, 349 frontend tests,
  two twice-run PostgreSQL acceptance tests, and two twice-run declared browser tests at commit
  `547c6835`; unchanged product gates were not repeated in this documentation-only review.
- One review-only contract probe fails on the intended assertion: a newer incoherent cross-
  application completion is rejected by the canonical member facade while the account facade still
  returns the older masked code decision.
- Static inspection records the full-portfolio projection/page-walk, one-row query ceilings,
  incomplete matrices, exact pending-only constraint, restored tab shell, and acceptance-test
  duplication/coverage boundaries.
- Evidence: `.ralph/runs/2026-07-19_104332_architecture_review/evidence/`.
- Epic audit: M07-FR-001-010 and M08-FR-001-011 retain implemented owners or explicit A-135 pending
  governance, but M07-FR-010 remains conditional on 009L4's canonical decision. `CONTEXT.md` remains
  truthful. No slice is marked `Blocked`, so no stale prerequisite required re-parking. No ADR was
  added because the corrective restores already binding owner/selector contracts.

Older findings and exact prior citations remain searchable in Git and retained review packets; they
are not repeated unless current code reproduces them.
