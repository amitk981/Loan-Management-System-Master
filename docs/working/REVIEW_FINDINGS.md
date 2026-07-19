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

## Open findings from 2026-07-19_041708_architecture_review

Reviewed product commits: `bc476293` (009H9D), `7e88fe42` (009J), and `eeb0ba7d` (009K), relative
to the previous architecture-review commit `c90cb326`. Epic 009 reaches its declared boundary in
this range, so M07/M08 functional-requirement coverage was audited in addition to the three diffs.

### 009L — Epic 009 staff workflow and SAP posting closure

- **High — the binding staff workflow is incomplete and partly non-executable:** 009K requires
  S36-S41 end to end, but its own run packet records S36 create/send as open and the workspace
  admits only Senior Finance/CFC. Its enabled S37 descriptor names nonexistent permission
  `finance.sap_customer_code.complete` instead of source/catalogue
  `finance.sap_request.complete`, marks optional completion facts required, and both S37 and
  transfer success submit raw `datetime-local` values although their real endpoints require aware
  ISO-8601 timestamps. The mock-bound frontend tests never assert those request bytes. Neither 009J
  nor 009K retained any of their four required real-Django screenshots, so the walkable/prototype
  acceptance claim is also unproved. This violates 009K requirements 1-4 and acceptance, screen spec
  S36-S41, API §§29-31/45, and the two slices' explicit visual contracts.
- **High — workspace authority and financial state are not current-owner truth:** CFC admission can
  fall back to raw `approval_authority_type` instead of the governed effective role; Senior Finance
  admission checks only initiate authority, then an uncaught `LoanAccountReadPermissionDenied`
  produces 500; and the Senior Finance path projects its newest mutable disbursement without the
  current-evidence check used by the CFC path. The retained review probes receive 500 for an admitted
  Finance actor and still receive one `approved` row after its immutable initiation ledger is made
  incoherent. This contradicts the 009K digest/API contract's exact current authority, server-owned
  action, safe blocker, and zero-fabrication promises.
- **High — M07-FR-009 is absent at the Epic 009 boundary:** source requires tracking the initial loan
  payment SAP entry. The digest traceability table covers M07-FR-001-008, readiness owns FR-010, and
  no model, API, slice, or explicit ASSUMPTIONS deferral owns FR-009. Payment success therefore has
  no honest pending/posted SAP obligation even though the epic is recorded complete.
- **Medium — 009J source/test fidelity is partial:** source §30.2 names search, status, member, and
  DPD filters, while the implementation rejects every parameter except page/page-size without an
  explicit Epic 010 deferral. Its required missing/duplicate/changed creation, terms, SAP, transfer,
  activation, cross-object, and balance/status drift matrix is mostly absent; retained tests cover
  one changed amount and inactive SAP case.
- **Medium — SAP/read architecture and query boundaries drifted:** the Loan Account 360 and
  disbursement coordinators import SAP persistence models and reconstruct current request/code
  truth outside `SapCustomerProfileModule`, reversing 009B3C's public-owner seam. Both account and
  workspace reads materialize the full scoped portfolio before slicing, then re-fetch/evaluate per
  row (readiness twice), so one-row tests hide unbounded duplication.
- **Medium — real and fixture account truth can be composed:** after loading a real 009J account,
  later `LoanAccount360` tabs fall back to `loanAccounts[0]` and render mock ledger/document/default
  facts plus local interest/closure calculations. This conflicts with 009J's “do not imply later
  owner truth” boundary and the frontend mock ratchet. 009L must make those tabs unavailable or
  explicitly non-production until existing final-removal owner 010M supplies real servicing truth.
- **Medium — the prior MP14 selection regression remains open:** no reviewed commit adds the required
  two finance-relevant applications in opposite list orders through unit and browser selection.

One root-owner corrective, `009L`, groups the S36-S41, workspace-authority/evidence, SAP-posting,
query/module-boundary, negative-matrix, MP14, and visual-proof symptoms. It is ordered after 009K and
before Epic 010; 010A depends on it so servicing cannot build on an unclosed disbursement boundary.

## Closed in this review

- `009H9D` validates every required queued template fact and keeps blank, malformed, drifted, or
  recomputed-checksum provenance legacy-partial/ambiguous instead of promoting it.
- `009H9D` enforces exact generic-versus-advice permission plus assigned ownership for exception
  collection, detail, and resolution; the three current copied contract tests pass.
- `009H9D` normalizes provider vocabulary to `email`/`sms` and implements strict stable pagination
  beyond 100 rows with standard validation/redaction.
- `009H9D` restores public communications-owner channel/adapter/job interfaces and observable
  Email/SMS/cross-channel idempotency tests without private Celery/process calls.

## Review evidence

- Current 009H9D closure tests: 3 passed. Retained 009J/009K backend tests: 10 passed. Focused 009J/
  009K frontend tests: 14 passed. Full product gates were not repeated in this documentation-only
  review; the unchanged product commits retain their orchestrator gate evidence.
- Two review-only Epic 009 probes fail on the intended assertions: admitted Senior Finance returns
  500, and an incoherent approved disbursement remains in the workspace. A direct contract check
  proves both real mutation owners reject the raw browser `datetime-local` timestamp.
- Evidence: `.ralph/runs/2026-07-19_041708_architecture_review/evidence/`.
- Epic audit: M07-FR-001-008/010 and M08-FR-001-011 have retained backend owners, but M07-FR-009 is
  missing and S36-S41 reachability/evidence is partial as above. `CONTEXT.md` remains truthful. No
  slice is marked `Blocked`, so no stale block required re-parking. No new ADR was needed because
  009L restores existing source and public-owner contracts rather than choosing a new architecture.

Older findings and exact prior citations remain searchable in the historical ledger; they are not
repeated here unless current code reproduces them.
