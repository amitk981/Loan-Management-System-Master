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

## AR-010-INTEREST-UI-001 — portfolio accrual silently excludes scoped loans after the first 100

Root: ROOT-010-INTEREST-PORTFOLIO-COMPLETENESS

Severity: High
Disposition: Carried
Reviewed boundary: `fff95e9d...71fd80df` (010N3)

010N3 traverses every reported page and discloses explicit 100-row batches, but its completeness
proof compares pagination metadata and row count only. A review probe returns stable
`total_count=101` metadata with loans 1–100 on page one and loan 100 again on page two. The shared
loader accepts 101 rows, and the portfolio runner then accepts the duplicate across its separate
100/1 batches and reports two completed batches even though only 100 unique loans were accrued.
Loan 101 is still silently absent from a successful complete-looking operation.

This is the same population-owner root, not a new finding. Corrective 010N6 must make stable unique
identity part of the shared complete-collection contract and validate the global selected set before
the first financial batch. Metadata drift, duplicate page boundaries, missing identities, and
cross-batch duplicates need permanent 1/100/101 tests; backend action projection debt remains
supporting Medium work under this root.
Reproducer: `.ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/interest-portfolio-identity.log`.

## AR-010-SEARCH-001 — sensitive global-search inputs bypass their domain authority

Root: ROOT-010-GLOBAL-SEARCH-SENSITIVE-AUTHORITY

Severity: High
Disposition: Carried
Reviewed boundary: `fff95e9d...71fd80df` (010N4)

010N4 introduces domain-named facades and closes the CFO-without-permission cheque probe, but the
security facade explicitly discards `actor` and queries every matching blank cheque, CDSL pledge, or
SH-4 row from permission membership alone. The canonical security-package owner additionally
requires effective role, Stage-4 evidence, and object scope. A real public probe grants cheque-manage
permission for a record whose application is not in canonical Stage 4; global search still exposes
its member with `total_count=1` where the owner contract requires zero.

Input routing also recognises SAP and CDSL only through invented `SAP-`/`CDSL-` prefixes even though
their stored identifiers accept other valid formats. The companion probe changes the authorised SAP
code to `CUST000123` and receives zero matches. The existing tests use only in-scope prefixed records
and exercise six-group boundaries through `paginate_group` rather than real owner queries. Corrective
010N7 must consume canonical input-owner decisions, object scope before disclosure, and arbitrary
valid identifier formats; bank/identity authority and dead compatibility-alias debt remain grouped
under this same root.
Reproducer: `.ralph/runs/2026-07-22_031437_architecture_review/evidence/review-probes/global-search-owner-scope.log`.

## AR-010-MIS-001 — quarterly MIS does not retain one authorised cutoff-owner decision

Root: ROOT-010-MIS-AS-OF-OWNER

Severity: High
Disposition: Carried
Reviewed boundary: `bbc8aa74...92053395` (010N5)

010N5 preserves two green cutoff-helper tests, but its new “real model” case constructs unsaved
`InterestInvoice` instances inside `SimpleTestCase` and calls private
`_invoice_status_at_cutoff`. It never persists the before/on/after lifecycle, generates a report
through the public MIS owner, mutates sources after generation, or replays that historical report.
The existing public replay test does not combine invoice lifecycle with post-cutoff mutation.

This is incomplete closure evidence for the inherited root, not a new finding. Successor 010N8 must
cross the public generate/detail/drill-down/export/replay seam with real invoice lifecycle records
and retain the same grouped repair episode.
Reproducer: `.ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/mis-public-owner-closure.log`.

## AR-010-REMINDER-001 — reminder eligibility and delivery do not retain one serviceable decision

Root: ROOT-010-REMINDER-DELIVERY-OWNER

Severity: High
Disposition: Carried
Reviewed boundary: `bbc8aa74...92053395` (010N5)

The repayment-after-check probe remains green and the trusted class still declares five cases, but
the recipient-source case changes the member mobile number and deletes the actor's loan-read role
permission in the same setup. It then asserts only `delivery_status`, not the provider call count.
A broken current-recipient binding can therefore remain green because the separate scope-revocation
branch cancels first; “at most one justified provider effect” is not proved for the source cause.

This is incomplete closure evidence for the inherited root. Successor 010N8 must isolate source and
scope causes and assert exact provider effects in every retained PostgreSQL case while keeping the
complete grouped repair episode.
Reproducer: `.ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/reminder-source-owner-closure.log`.

## AR-010-DPD-001 — current DPD and historical policy evidence are not relationally bound

Root: ROOT-010-DPD-SNAPSHOT-OWNER

Severity: High
Disposition: Closed
Reviewed boundary: `5c0aba87...283d9767` (010K3)

010K3 adds database enforcement on both pointer writes and snapshot reparenting, rejects mutation of
an approved active policy, and routes current DPD through the public capitalisation-aware source
decision. The current focused closure set passes the two original root obligations: cross-account
snapshot/policy integrity and classification of capitalised interest exactly once. The product run's
same owner-boundary class also passed its five PostgreSQL cases twice. Reminder date/batch coverage
and remaining fixture coupling are retained under their own roots and do not reopen this DPD owner.
Reproducer: `.ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/dpd-owner-reproducer.log`.
Closure evidence: `.ralph/runs/2026-07-21_134356_architecture_review/evidence/review-probes/dpd-owner-closure.log`.

## AR-010-INTEREST-001 — interest calculation and replay do not retain one as-of financial decision

Root: ROOT-010-INTEREST-CALCULATION-OWNER

Severity: High
Disposition: Closed
Reviewed boundary: `b7dbc27b...af2ece48` (010H3)

010H3 freezes every approved calculation-policy mutation path, retains rounding mode/precision/
whole-decision boundary, and fails closed when policy is absent. Capitalisation now requires exact
invoice, account, schedule, ledger, payment, and principal-increment agreement before any financial
or communication evidence commits. The focused closure run passes three policy tests and four
independent mismatch/zero-write matrices. The distinct DPD failure to consume successful
capitalisation evidence remains under `AR-010-DPD-001`; it does not reopen this calculation owner.
Reproducer: `.ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/interest-owner-reproducer.log`.
Closure evidence: `.ralph/runs/2026-07-21_054048_architecture_review/evidence/review-probes/interest-owner-closure.log`.

## AR-010-ALLOCATION-001 — allocation admits unposted and unapproved financial effects

Root: ROOT-010-ALLOCATION-ADMISSION

Severity: High
Disposition: Closed
Reviewed boundary: `2944b3ea...34ac6b75` (010E3)

010E3 stores the exact allocation response in immutable decision evidence and replay reads that
snapshot after the receipt later becomes reversed. The focused public regression passed with the
statement and rate closure set; changed and cross-receipt keys remain zero-write conflicts. The
broader private-fixture concern is retained under `AR-010-SERVICING-SEAM-001`, not charged back to
this financial-admission root.
Closure evidence: `.ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/allocation-closure.log`.

## AR-010-STATEMENT-001 — statement evidence is orphanable and bypasses match scope

Root: ROOT-010-STATEMENT-EVIDENCE

Severity: High
Disposition: Closed
Reviewed boundary: `2944b3ea...34ac6b75` (010E3)

`_subsidiary_narration_is_ambiguous` now checks both competing application references and competing
borrower identities. The focused public matrix passes exact, missing, conflicting-application, and
conflicting-borrower branches without weakening direct-receipt matching. Test-fixture architecture
remains independently carried under `AR-010-SERVICING-SEAM-001`.
Closure evidence: `.ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/statement-closure.log`.

## AR-010-RATE-001 — effective-rate owner permits retroactive and mutable financial truth

Root: ROOT-010-RATE-VERSION-OWNER

Severity: High
Disposition: Carried
Reviewed boundary: `016a3a89...28f8e19d` (010E4)

010E4 closes fabricated-active bulk paths, future activation's immediate projection write, frozen
activation replay, and the changed rate-to-loan public facade. The stable root nevertheless recurs
at current-date ownership. Its convergence facade accepts a caller's arbitrary future
`as_of_date`; the retained probe publishes a 1 September successor into the current projection on
20 July instead of rejecting the early mutation. Conversely, repository search finds no production
caller or due-date runtime owner for that facade, so without an ad-hoc caller the stored projection
remains stale after the successor becomes effective. Collection filters can then omit an account
before the canonical resolver sees it.

This root has used ordinary generations 1 (`010E3`) and 2 (`010E4`). The standing one-terminal-
successor policy admits `CR-014` as its only Architecture Review Finalizer; it groups server-current-
date enforcement, the production due-date owner, collection/scalar/interest-consumer equivalence,
and idempotent PostgreSQL races. Another recurrence after `CR-014` must fail closed rather than
create a second terminal or numeric leaf.
Reproducer: `.ralph/runs/2026-07-20_194456_architecture_review/evidence/review-probes/rate-current-date.log`.

## AR-010-LEDGER-001 — ledger pagination materializes the full servicing history

Root: ROOT-010-LEDGER-PAGINATION

Severity: Medium
Disposition: Carried
Reviewed boundary: `2944b3ea...34ac6b75` (010E3/010H)

010E3 replaces unconditional full-history reads with prefix limits and proves correct 1/21/101 row
results, but it does not implement the promised database page window. `get_ledger` fetches each
movement family from row zero through `movement_end`, adds capitalisation as a third prefix, sorts in
Python, and only then applies `movement_start`. Deep pages therefore still scale with the offset and
the 101-row test does not assert page-bounded fetch counts.

This Medium performance debt stays with the Epic 010 servicing-read closure; it does not create an
immediate financial corrective slice.
Reproducer: `.ralph/runs/2026-07-20_121921_architecture_review/evidence/review-probes/ledger-pagination.log`.

## AR-010-SERVICING-SEAM-001 — servicing evidence and tests bypass public owner seams

Root: ROOT-010-SERVICING-OWNER-SEAM

Severity: High
Disposition: Carried
Reviewed boundary: `bbc8aa74...92053395` (010N5)

010N5 removes the capture-only browser coordinator and the original one-request probe is green.
However, the replacement validator checks only exact top-level keys plus
`capture.repayment_id` and `allocation.repayment_allocation_id` before casting the rest of the
payload. A current executable probe supplies identifier-only nested objects and a second response
whose allocation names a different repayment; both resolve as successful complete outcomes.

The backend additions cover exact replay, changed payload, allocation rollback, and an equal-key
race, but the crash test never retries and no test proves one retained SAP decision, full response,
ledger/balance effect, or audit result across capture/SAP/allocation/response boundaries. Successor
010N8 must enforce the complete relational response contract and finish that public-command matrix,
retaining all three inherited roots in the same episode.
Reproducer: `.ralph/runs/2026-07-22_055158_architecture_review/evidence/review-probes/servicing-composite-contract.log`.

## Targeted closure review 2026-07-19_193824_architecture_review — Epic 009 generation 2

Reviewed product commit: `4f8febd3` (009L7), relative to successful architecture-review commit
`e748f8ca`. This review was limited to the final corrective diff, the active 009L7 finding lineage,
and its declared acceptance evidence.

### Result — convergence failure; fail closed

- **Retained High — the owner/selector root still exposes evidence its scalar owner rejects:**
  `filter_accounts_with_current_transfer` in `post_transfer_evidence.py:51-81` admits an active
  account from coarse disbursement/related-row existence fields, while
  `completed_success_is_coherent` at `disbursement_transfer_success.py:609-821` additionally owns
  exact transfer-file provenance, register/advice/posting relations, audit/workflow bodies, actor,
  history, and activation evidence. `loan_account_360.py:161-216` now treats the selector as final
  and no longer consumes that owner. A review-only public HTTP probe changes the retained transfer
  document checksum, first proves `resolve_post_transfer_evidence` returns `None`, then receives
  `total_count: 1`, the active row, and detail `200` instead of zero rows and `404`. This is the same
  root-owner recurrence mapped through 009L4-009L7, not a new finding.
- **Retained High — exact object scope is only partially restored:** 009L7 correctly requires
  `finance.loan_account.read`, so initiation authority alone no longer opens list/detail. However,
  `loan_account_read.py:65-77` still starts Senior Finance scope from any assigned request and CFC
  scope from raw task/status rows; `loan_account_360.py:91-104` skips the latest-assignee restriction
  when the reader also holds initiation authority and removed the exact scalar scope resolver.
  Thus the permission substitution is fixed but the active finding's current-object-scope contract
  remains conditional. This is another symptom of the same retained owner-boundary root.
- **Retained High symptom — combined workspace still counts before a later drop:**
  `disbursement_workspace.py:93-140` counts initiation candidates, while lines 203-205 and 264-299
  later resolve a latest disbursement and silently omit a projection when its scalar current owner
  rejects it. Requirement 2's count/page/body identity is therefore still not one decision.
- **Retained Medium — the executable five-branch matrix remains partial:** the new convergence
  suite adds six substantive one-row HTTP tests, but not S36/S37/combined/CFC 1/21/101 portfolios,
  more than four adjacent invalids, complete page edges, every scalar component/consumer, paired
  actions and mutations, stable query ceilings, or independent 400/403/404/409 behavior. Existing
  21/101 coverage remains Loan-Account-only.
- **Retained Medium — the browser fixture's public seam is only indirection:**
  `identity/epic009_e2e_fixture.py:14-26,43` imports a `TestCase`, calls `setUp`, and invokes private
  `_real_owner_initiation_fixture` and `_user` helpers. The new source-inspection test examines only
  the management command, so it misses the transitive codebase-design §26 violation.
- **Retained Low — duplicated selector/test helpers remain:** JSON key/equality expressions are
  copied across owner modules, and new tests continue to instantiate other `TestCase` fixtures.

009L7 is already the final grouped repair admitted for this corrective cycle. No third leaf
corrective or completed-slice mapping is valid. Ralph must stop at the Epic 009 boundary; owner-level
architecture work must replace the partial SQL-predicate/scalar-owner split with one materialized or
otherwise complete owner decision before Epic 010 can begin.

## Closed in this review

- **Ordinary/full Playwright fixture union:** `playwright.seed.ts` selects the union of staff,
  portal, and Epic 009 fixture families; the focused three-test seed suite passes, and retained full
  collection evidence covers 35 tests from 20 files.
- **Permission-gate portion only:** an initiator without `finance.loan_account.read` now receives the
  required `403`. This is a verified sub-closure, not a closed finding, because exact current object
  scope remains open above.

## Review evidence

- Independent Standards and Spec passes reviewed `git diff e748f8ca...HEAD` and agree that the same
  owner-boundary root and declared matrix/fixture obligations remain incomplete.
- Retained 009L7 regressions pass: 6 backend tests. The focused Playwright seed suite passes: 3
  tests. Both trusted browser manifests independently verify all nine retained PNGs.
- The review-only public transfer-file probe fails on its intended assertion with
  `(total_count=1, one row, detail=200)` instead of `(0, [], 404)` after the canonical transfer owner
  rejects the checksum-drifted evidence.
- Evidence: `.ralph/runs/2026-07-19_193824_architecture_review/evidence/`.
- Epic audit: M07-FR-001-010 and M08-FR-001-011 retain implemented owners or explicit A-135
  pending-posting governance, but their public collection/read truth remains conditional on the
  unresolved owner boundary. `CONTEXT.md` remains truthful. No slice is marked `Blocked`, so no
  stale prerequisite required re-parking. No ADR was added because no new durable design decision
  was accepted; this review rejects a recurrence of the already binding owner contract.

## Open findings from 2026-07-19_180917_architecture_review

Reviewed product commits: `50d91369` (009L6) and `fe4b0ecb` (CR-012), relative to successful
architecture-review commit `399fb954`. The intervening `d17954b8` changes Ralph orchestration and
is outside this targeted product-closure critique. Normal/repair attempts and mechanical state,
progress, handoff, and retained run artifacts were treated as evidence rather than separate slices.

### 009L7 — Epic 009 read-boundary convergence closure

- **Retained High — the owner/selector root remains open after 009L6:** requirements 1-3 say every
  identity selected before count/offset must consume the same complete owner decision as its scalar
  projector, including send, file-integrity, completion, audit/workflow, readiness, bank/source,
  and aggregate facts. `filter_current_account_completions` in
  `sap_customer_profile.py:611-696` validates the completion manifest but omits the completed
  request's send-delivery owner that `_current_completed_code_evidence` rechecks at lines 700-813.
  `_assigned_workspace_requests` at lines 389-507 checks Annexure-I metadata but not the actual
  verified workbook/file integrity required by `_current_send_evidence` at lines 766-854. Two
  public review probes independently drift a completed account's send communication and an S37
  request's file checksum: both envelopes report `total_count: 1` while projection returns `[]`.
  This is the same active root-owner symptom mapped to 009L6, not a newly relabelled finding.
- **High — initiation authority now widens the public Loan Account read contract:** 009L6 changed
  `loan_account_read.py:28-61` so Senior Finance plus `finance.disbursement.initiate` substitutes
  for `finance.loan_account.read` and immediately returns the entire portfolio. The public list and
  detail views use that owner directly; list projection at `loan_account_360.py:124-145` does not
  reapply assignment scope. A review probe using the retained real initiation fixture receives
  `200` plus an eligible Loan Account without the read permission, where auth §34.7 and the binding
  API contract require `403` and current SAP-assignment scope. This is a new authorization and
  nondisclosure regression, not merely missing test coverage.
- **Carried Medium — the declared five-branch matrix is still partial:** requirement 5 names mixed
  1/21/101 portfolios for Loan Account, S36, S37, combined Senior Finance, and CFC, more than four
  adjacent drifts, all scalar components/consumers, paired action/mutation behavior, query ceilings,
  and independent error surfaces. 009L6 adds ten one-row equivalence tests and four PostgreSQL
  examples; the 21/101 and >4-row cases remain Loan-Account-only, and there is no equivalent
  S36/S37/combined/CFC matrix. This is the previously carried Medium, not a new finding.
- **Medium — the CR-012 runtime seed crosses private test seams:** guarded command
  `seed_epic_009_e2e_fixture.py:101-163` imports a `TestCase`, invokes `setUp`, and calls private
  `_real_owner_initiation_fixture`, `_grant`, and `_user` helpers. The guards contain operational
  exposure, but codebase-design §§26/42 require runtime callers and long-lived tests to consume a
  public owner interface; ordinary test refactors can now break browser provisioning.
- **Medium — ordinary full Playwright execution omits the Epic 009 seed:**
  `playwright.config.ts:31-40` selects the Epic 009 seed only when that filename appears in argv,
  while `testMatch` at lines 43-44 includes the spec in `npm run e2e`. An all-spec run therefore
  provisions the older fixture family but still collects the Epic 009 contract, contrary to the
  advertised README command. Targeted trusted acceptance passes and is not invalidated by this
  distinct full-suite configuration defect.
- **Low — selector helpers and test fixtures remain duplicated across seams:** `_JsonObjectKeyCount`
  and `_JsonValuesEqual` are copied in lifecycle, SAP, and disbursement owners; several tests
  instantiate other `TestCase` classes and private helpers. Assertions are substantive, but the
  repetition weakens locality under codebase-design §§26/42 and contributed to the partial-rule
  recurrence.

The one additional root repair permitted in this corrective cycle is `009L7`. It groups the
retained selector root, the new read-authorization regression, the executable matrix, and CR-012's
fixture/config boundary instead of adding leaf patches. `010A` now depends on 009L7. A recurrence
of this same root after 009L7 must fail closed under the bounded-generation policy.

## Closed in this review

- **PostgreSQL prerequisite ownership:** migration 0010 now records whether this app created
  `pgcrypto`, reverses only app-owned creation, and the declared four-test exact-selector label ran
  twice on PostgreSQL. The prior unsafe unconditional extension reversal finding is closed.
- **Public portal test seam:** the other-application SAP completion regression now exercises the
  authenticated portal HTTP contract instead of importing `_current_pre_payment_stages`. The prior
  private-helper finding is closed.
- **Duplicate PostgreSQL discovery:** the empty duplicate acceptance subclass was removed and
  replaced by one declared four-test production label. The prior duplicate-discovery finding is
  closed.
- **CR-012 browser evidence:** both trusted runs use real form login and owned Django endpoints,
  retain all nine declared structurally valid PNGs, and produce manifests with nine distinct hashes
  that exactly match the retained files. No owned-API route fulfilment is present. The new fixture
  architecture/full-suite observations above do not negate the targeted browser acceptance.

## Review evidence

- Independent Standards and Spec passes reviewed `399fb954..50d91369` and
  `d17954b8..fe4b0ecb` separately. Both identify the authorization regression and continuing
  selector/scalar split; the Spec pass finds CR-012's targeted contract complete.
- Three review-only public HTTP probes fail on the intended assertions: two report `(1, [])` rather
  than `(0, [])` after send/file drift, and an initiator without `finance.loan_account.read`
  receives `200` plus a Loan Account rather than `403`.
- CR-012's two nine-file manifests independently pass SHA-256 verification, contain nine distinct
  values, and name only valid PNGs. Prior independent validation retained 1,311 backend tests under
  coverage, 352 frontend tests, and two successful trusted browser runs.
- Evidence: `.ralph/runs/2026-07-19_180917_architecture_review/evidence/`.
- Epic audit: M07-FR-001-010 and M08-FR-001-011 retain implemented owners or explicit A-135
  pending-posting governance, but collection and public authorization truth remain conditional on
  009L7. `CONTEXT.md` remains truthful. No slice is marked `Blocked`, so no stale prerequisite
  required re-parking. No ADR was added because 009L7 restores already binding owner, permission,
  test-seam, and execution contracts rather than selecting a new durable business rule.

## Open findings from 2026-07-19_133456_architecture_review

Reviewed product commit: `1de7c16c` (009L5), relative to successful architecture-review commit
`6d3cdae1`. The product run and its repair form one committed slice boundary; mechanical Ralph
state, progress, handoff, and retained run artifacts were excluded from the product critique.

### 009L6 — Epic 009 owner-selector equivalence and matrix closure

- **High — 009L5 patches four named fields but still counts broader identities than its owners
  project:** requirement 1 says count, pages, offsets, and rows consume the exact owner decision,
  and requirement 2 forbids incoherent evidence from affecting totals or reachability.
  `loan_account_lifecycle.py:81-174` admits audit evidence whose team shape, exact key set, request
  shape, or SAP snapshot will fail `_created_account_decision` at lines 256-306;
  `sap_customer_profile.py:325-389` checks a send checksum and coarse relations before pagination
  while `_current_send_evidence` at lines 614-702 still rejects exact audit, task, workflow,
  workbook, actor, and delivery drift; and `current_disbursement_evidence.py:33-71` checks only a
  subset of the frozen-owner, initiation-ledger, task, and aggregate rules at lines 113-126 and
  161-263. `loan_account_360.py:98-140` and `disbursement_workspace.py:173-203` count and offset
  those broader sets, then silently drop rows through the scalar projectors. Four independent
  review probes change an omitted lifecycle team field, SAP completion body, SAP send body, and
  initiation maker-team field: every envelope still reports `total_count: 1` after the public
  scalar owner suppresses the body. This is the same root-boundary failure recurring after 009L4
  and 009L5, not four leaf defects.
- **Medium — the PostgreSQL selector prerequisite is neither ownership-safe nor production-proven:**
  `0010_enable_pgcrypto_for_exact_selector.py:4-11` uses `CREATE EXTENSION IF NOT EXISTS`, so the
  migration cannot know it created `pgcrypto`, but reversal unconditionally drops the shared
  extension. A rollback can remove pre-existing database infrastructure or fail when another
  consumer depends on it. The 009L5 slice declares runtime capability `none`, so its new
  PostgreSQL-only digest prerequisite has no declared PostgreSQL acceptance label; SQLite
  compatibility and a local smoke do not prove the production query path.
- **Low — the portal regression crosses the private helper seam:**
  `test_portal_disbursement_status_api.py:804-833` imports and directly tests
  `_current_pre_payment_stages` even though the application edge is observable through the portal
  HTTP contract. Codebase-design §26.1 says long-lived tests use the module interface when behavior
  is observable there. The assertion is real, but it does not prove the public authentication,
  object-scope, envelope, and timeline composition path.

The prior Medium executable-matrix finding remains open: 009L5 adds only six focused regressions,
not the required S36/S37/combined-Senior-Finance/CFC 1/21/101 portfolios, full invariant drift
matrix, action/mutation parity, or independent 400/403/409 surfaces. The prior Low empty-subclass
duplicate PostgreSQL discovery also remains open. These carried findings are not counted as new;
009L6 groups them with the selector boundary instead of creating more leaf work.

New corrective `009L6` replaces patch-per-field selectors with an owner-selector equivalence
boundary and absorbs the matrix, test-seam, PostgreSQL-proof, and safe-extension-ownership work. It
depends on 009L5; `CR-012` and `010A` now depend on 009L6 so final hosted proof and servicing cannot
build on incorrect Epic 009 collection truth.

## Closed in this review

- **Portal application edge:** all five retained 009L4 probes are green, including the case where a
  coherent completion for another application cannot complete the requested application's SAP
  stage. The completed-request edge remains compatible with reusing the member's retained code on
  a newly completed request for the current application.
- **Duplicated lifecycle scalar validator:** `_resolve_created_account` now delegates to the same
  `_created_account_decision` implementation as bounded bulk resolution. The distinct selector
  equivalence defect above remains open.
- **Django private `_state` fixture copying:** the changed Loan Account tests now use a public
  constructor-based `_copy_for_insert` helper. The newly introduced private portal-helper test is a
  different, lower-severity interface-test issue.

## Review evidence

- Independent Standards and Spec passes reviewed `git diff 6d3cdae1...HEAD` separately and both
  identified the partial selector/scalar boundary; the Spec pass also confirmed the required
  workspace/action/error matrix remains incomplete.
- The five retained 009L4 probes pass. Four new review-only probes fail on their intended
  assertions: lifecycle, SAP completion, SAP send, and CFC bodies are suppressed while every
  pagination envelope reports one stale identity. No production file was changed.
- Prior independent validation for commit `1de7c16c` retained 1,294 backend tests under coverage,
  351 frontend tests, Django check, migration sync, and the focused repair proof.
- Evidence: `.ralph/runs/2026-07-19_133456_architecture_review/evidence/`.
- Epic audit: M07-FR-001-010 and M08-FR-001-011 retain implemented owners or explicit A-135
  pending-posting governance, but collection/read truth remains conditional on 009L6. `CONTEXT.md`
  remains truthful. No slice is marked `Blocked`, so no stale prerequisite required re-parking. No
  ADR was added because 009L6 restores the already binding owner/selector interface instead of
  choosing a new durable business rule.

## Open findings from 2026-07-19_123045_architecture_review

Reviewed product commit: `3b31edc4` (009L4), relative to successful architecture-review commit
`f8eb78be`. The prior independently validated product run and its two repairs are one committed
slice boundary; mechanical Ralph artifacts were excluded from the product critique.

### 009L5 — Epic 009 exact selector and consumer parity closure

- **High — exact collection identities still disagree with totals and offsets:** 009L4 requirements
  2-3 say count and database pagination operate on the exact eligible identity set, with incoherent
  rows affecting neither totals nor reachability. `loan_account_360.py:104-147` counts and offsets a
  queryable superset before scalar lifecycle/SAP/transfer reconciliation. The lifecycle selector
  omits exact JSON-shape and nonempty actor-role checks enforced later at
  `loan_account_lifecycle.py:255-305`; the SAP selector similarly omits the completion/send digest,
  actor, assignment, workbook, and exact audit checks enforced at
  `sap_customer_profile.py:539-652`. S37 counts its coarse send query before dropping rows through
  `_current_send_evidence`, and the CFC branch at `disbursement_workspace.py:171-203` counts raw
  pending task rows before `_disbursement_is_current`. Four retained review probes independently
  drift creation roles, completion digest, send checksum, and initiation evidence: every body is
  suppressed, but every pagination envelope still reports `total_count: 1`. A four-row overscan
  cannot repair a false positive before the requested offset, so totals leak existence and later
  valid rows can shift or strand.
- **High — the member portal does not enforce the canonical application edge:** requirement 1 says
  every consumer delegates to one member/application/customer-code completion decision and rejects
  cross-application evidence identically. `_current_pre_payment_stages` in
  `portal_disbursement_status.py:462-472` checks only member and active status; it never compares
  `sap.loan_application_id` with the requested application. A review-only unit probe supplies a
  coherent current completion for another application and the requested application's `sap_setup`
  stage incorrectly becomes true. This can advance an application's borrower-visible finance stage
  on evidence that Loan Account/readiness consumers reject, leaving M07-FR-010 conditional.
- **Medium — the lifecycle owner now has two scalar evidence validators:**
  `loan_account_lifecycle.py:255-325` adds `_created_account_decision` for bulk reconciliation while
  the prior single-row validator remains around lines 367-436 with substantially duplicated field,
  audit, workflow, and projection checks. Codebase-design §§26/42 require one testable owner
  interface and centralised workflow rules; the duplication is already a likely source of selector
  drift and should collapse while the High selector defect is corrected.
- **Low — new acceptance tests overstate their interface fidelity:** the 101-row pagination fixture
  in `test_loan_account_reads_api.py:314-402` copies Django private `_state` and immutable-ledger rows
  rather than using the owner interface required by codebase-design §26. The MP14 test at
  `MP14_DisbursementStatus.test.tsx:128-150` calls its case “surrounding list order” but only swaps
  one explicit-id prop; it does not model a surrounding list. The assertions are real for their
  narrower behavior, but they do not close the named matrix by themselves.

The prior Medium executable-matrix finding remains open: 009L4 added 1/21/101 Loan Account cases,
but not equivalent S36/S37/Senior-Finance/CFC portfolios, more-than-four drift runs, the full
consumer/action/mutation matrix, transport bytes, or independent 400/403/409 surfaces. The prior
Low empty-subclass duplicate PostgreSQL discovery also remains open. These carried findings are not
counted as new; both naturally fold into 009L5 rather than creating leaf slices.

New corrective `009L5` groups the selector, portal-consumer, duplicated-validator, and executable-
proof symptoms at the Epic 009 read boundary. It depends on 009L4; `CR-012` and Epic 010 now depend
on 009L5 so hosted browser proof and servicing cannot build on known incorrect product truth.

## Closed in this review

- **Member/account facade divergence:** `get_account_customer_code` now delegates to
  `get_customer_code_for_member`, so the exact prior newer-incoherent cross-application probe is
  green for those two consumers. The newly found portal application-edge defect is distinct and
  remains owned by 009L5.
- **Full-portfolio projection and page walking:** Loan Account and combined Senior Finance reads now
  issue database count/offset/limit queries and reconcile only the page plus a constant window.
  Work no longer scales by deeply projecting the entire portfolio, although the new High finding
  means the bounded identity set and its reported totals are not yet exact.

## Review evidence

- Independent Standards and Spec passes reviewed `git diff f8eb78be...3b31edc4` separately; both
  identified the selector/count boundary, and the Spec pass identified the portal consumer gap.
- Five review-only probes fail on their intended assertions: four envelopes report one stale row
  after their projector rejects it, and one portal application accepts another application's SAP
  completion. No production file was changed.
- Prior independent validation for commit `3b31edc4` retained 1,288 backend tests under coverage,
  349 frontend tests, all frontend gates, Django check, migration sync, and the focused repair proof.
- Evidence: `.ralph/runs/2026-07-19_123045_architecture_review/evidence/`.
- Epic audit: M07-FR-001-009 and M08-FR-001-011 retain implemented owners or explicit A-135 pending
  governance; M07-FR-010 remains conditional on 009L5's exact application edge and selector truth.
  `CONTEXT.md` remains truthful. No slice is marked `Blocked`, so no stale prerequisite required
  re-parking. No ADR was added because 009L5 restores already binding owner/selector contracts.

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
