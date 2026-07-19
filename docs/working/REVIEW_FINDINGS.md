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

## Open findings from 2026-07-19_093632_architecture_review

Reviewed product commit: `de3d0f0c` (009L), relative to successful architecture-review commit
`4e44116d`. Later commits on `staging` are Ralph infrastructure/queue maintenance rather than
completed product slices. Epic 009's M07/M08 boundary was re-audited because 009L was its closure.

### 009L3 — Epic 009 authority, evidence, and pagination closure

- **High — Loan Account scope/evidence is applied after count and database slicing:**
  `loan_account_360.list_accounts` counts and slices the broad role-qualified queryset before
  `account_is_scoped` and immutable `_project` checks, then subtracts only invalid rows on the
  current page. Denied/incoherent accounts therefore affect totals and page reachability, can leave
  an empty page while later valid rows are stranded, and disclose portfolio shape across object
  scopes. This violates the working 009J contract's explicit “scope before pagination” rule,
  auth §19.3 nondisclosure, and 009L requirement 6.
- **High — action and SAP evidence decisions still differ across public owners:** three current
  review probes fail. A second Credit Manager can successfully invoke the canonical create mutation
  but receives zero S36 rows because the new selector narrows candidates to intake creator/receiver.
  A primary-role CFC whose governed `approval_authority_type` is removed still receives authorise/
  reject actions that the mutation rejects. After a SAP completion audit digest is changed, the
  canonical member facade returns no code while new `get_account_customer_code` still returns it.
  These reproduce the prior authority/current-evidence root and add the S36 reachability defect;
  they contradict auth §§16.3/19.2/20.1 and 009L requirements 1-3.
- **High — the new posting ledger can fabricate SAP success:** A-135 and 009L require confirmation
  to remain unavailable until governance names an actor, permission, adapter, and immutable
  acceptance evidence. The model nevertheless permits `posted` with only a mutable reference/time,
  and `completed_success_is_coherent` accepts that shape without actor, grant, adapter, provider/
  manual evidence, audit, or workflow truth. Pending M07-FR-009 tracking exists, but its false
  terminal state is a financial/data-integrity contract violation.
- **Medium — query/test closure remains portfolio-shallow:** the workspace still walks every
  Loan Account page, materializes all SAP/CFC rows, re-fetches accounts/disbursements/banks, and
  evaluates readiness twice before Python slicing. Its query ceilings use one row. The declared
  009J drift matrix, 009K action-parity matrix, and MP14 opposite-order unit/real-browser selection
  remain incomplete. The retained PostgreSQL race test does not assert an
  `InitialLoanPaymentSapPosting` count even though the post-completion digest says it proves one.
- **Medium — Loan Account 360 was redesigned instead of safely unwired:** removing mock servicing
  facts was correct, but 009L deleted the established tabbed 360 composition and replaced it with a
  facts grid plus lock card. That exceeds the allowed visibility/data changes and conflicts with
  `FRONTEND_DESIGN_RULES.md`'s no-layout-redesign rule. Existing tabs must remain in the approved
  shell with their 010M-owned bodies explicitly unavailable and fixture-free.

`009L3` groups the product root boundary: action/mutation parity, canonical SAP evidence, scope-first
pagination, pending-only posting truth, populated matrices, and prototype-safe unavailability. It
depends on 009L and is ordered before both CR-012 and Epic 010.

### CR-012 — Epic 009 trusted-browser evidence

- **High — 009L's retained browser pass does not execute the declared real workflow:** the spec
  injects a token, fulfils auth/workspace/Loan Account routes in Playwright, mutates local objects,
  never submits S36-S41 actions, and fabricates its 503. It omits the required Loan Account list
  screenshot; SAP confirmation, readiness, and initiation PNGs have the same SHA-256. The passing
  run therefore cannot prove real Django authority, request bytes, 400/403/409, duplicate UTR,
  replay, refresh, or distinct UI states. Existing Not Started corrective `CR-012` exactly covers
  this new evidence finding and now depends on 009L3; no duplicate corrective was added.

## Closed in this review

- M07-FR-009 now has one atomic singular pending obligation linked to the transfer, register,
  application, account, member, amount, action, and evidence digest. The missing-capability finding
  is closed; 009L3 separately removes the unsupported evidence-free `posted` state.
- Loan Account 360 no longer composes a real selected account with another borrower's mock repayment,
  interest, default, document, or closure facts. The truth-composition finding is closed; the new
  layout-fidelity finding above owns how the safe unavailable state is presented.

009L also fixed the prior Senior Finance 500, incoherent-disbursement projection, supported filters,
and aware timestamp serialization, but those were symptoms inside broader findings that remain open
until the matrices and exact owner parity above close.

## Review evidence

- Retained current tests remain green: 43 focused backend tests passed with 2 PostgreSQL-only skips;
  19 focused frontend tests passed. Full product gates were not repeated in this documentation-only
  review; `de3d0f0c` retains the orchestrator's authoritative coverage and browser gate records.
- Three review-only contract probes fail on the intended assertions: mutation-authorised S36 row
  omission, CFC action widening, and cross-facade SAP evidence disagreement.
- Static evidence records the post-slice pagination order, posting lifecycle acceptance, mocked
  browser routes, and screenshot hashes. Three of eight screenshots are byte-identical.
- Evidence: `.ralph/runs/2026-07-19_093632_architecture_review/evidence/`.
- Epic audit: M07-FR-001-010 and M08-FR-001-011 now have retained owners or explicit A-135 pending
  governance, subject to the open correctness/evidence findings above. `CONTEXT.md` remains truthful.
  No slice is marked `Blocked`, so no stale prerequisite required re-parking. No ADR was added: both
  correctives restore binding source/public-owner/frontend contracts rather than choosing a new
  durable architecture.

Older findings and exact prior citations remain searchable in Git and retained review packets; they
are not repeated unless current code reproduces them.
