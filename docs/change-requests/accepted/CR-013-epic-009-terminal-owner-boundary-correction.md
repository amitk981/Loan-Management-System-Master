# Close the Epic 009 owner boundary without exposing stale or unowned accounts

## Type
bug-backend

## Severity
High

## What Is Happening
The final Epic 009 review proved that Loan Account collections can count and expose an active
account after the canonical transfer owner rejects its evidence. Changing the retained transfer
document checksum makes `resolve_post_transfer_evidence(...)` return no valid owner, but the public
list still reports one row and public detail still returns HTTP 200 instead of zero rows and 404.
The combined Senior Finance workspace can similarly report `(total_count=1, rows=[])` because it
counts a stale initiation candidate before projection rejects it. Senior Finance and CFC scope is
still assembled from partial assignment/task predicates rather than one exact current owner
decision shared by counts, rows, details, actions, and mutations.

The review also proved that `sap_workflow.0002` gives historical completed SAP requests an empty
delivery checksum while current selection requires a valid 64-character snapshot, causing a
previously valid completed account to disappear after migration. The Epic 009 E2E fixture builder
still imports a private Django `TestCase`, invokes `setUp`, and calls private test helpers. A fresh
ordinary full-suite seed union can fail on a duplicate `DocumentTemplate`. Finally, the promised
five-collection 1/21/101 and adjacent-invalid matrix remains represented mostly by one-row tests.

These are retained root-boundary failures from corrective generation 2. They must be closed by one
owner-level correction before Epic 010; they must not be split into recurring leaf review slices.

## Expected Behaviour
One backend-owned eligibility decision must validate every binding account, SAP, disbursement,
transfer, file, actor, assignment, task, audit, workflow, and communication fact before an identity
is counted or exposed. Public lists, pagination counts, rows, details, available actions, and
mutations must consume that same decision. If the canonical owner rejects the account, all read
and write surfaces must consistently hide or reject it without count/row disagreement.

Historical coherent SAP completion must survive the additive checksum migration through a safe,
deterministic backfill or reconciliation rule. Runtime E2E fixture code must use public fixture or
domain builders and must not import test modules or private `TestCase` helpers. The complete E2E
seed family union must run on a fresh database in any supported order without uniqueness failures.

## Steps To Reproduce
1. Use the retained review probe from
   `.ralph/runs/2026-07-19_193824_architecture_review/evidence/review-probes/` to create a valid
   active Loan Account, change its retained transfer-file checksum, and confirm the canonical
   transfer owner returns no evidence.
2. Request the public Loan Account list and detail. Observe total count 1, one exposed row, and
   HTTP 200 instead of total count 0, no rows, and HTTP 404.
3. Use the retained generation-2 review probe for a stale Senior Finance initiation candidate.
   Observe `(1, [])` rather than `(0, [])`.
4. Create a coherent completed SAP request using the pre-`sap_workflow.0002` state, apply the
   migration's historical default, and request the public Loan Account list. Observe the account
   disappear because the checksum snapshot is empty.
5. Inspect `sfpcl_credit/identity/epic009_e2e_fixture.py`. Observe the import from
   `sfpcl_credit.tests`, `TestCase.setUp()`, and private fixture/helper calls.
6. Run the fresh staff + portal + Epic 009 E2E seed union retained by review run
   `2026-07-19_192334_architecture_review`. Observe the duplicate governed `DocumentTemplate`
   uniqueness failure unless the fixture order happens to avoid it.

## Where It Appears
Public Loan Account list/detail APIs; S36, S37, combined Senior Finance, and CFC workspace
collections and their actions; Epic 009 SAP/disbursement/transfer owner selectors; the
`sap_workflow.0002` migration path; and Epic 009/full-suite E2E fixture seeding.

## Source Document Reference
`docs/source/functional-spec.md` M07-FR-001 through M07-FR-010 and M08-FR-001 through M08-FR-011;
`docs/source/auth-permissions.md` §§19.3 and 34.7; `docs/source/codebase-design.md` §§16, 26, and 42;
`docs/slices/009L7-epic-009-read-boundary-convergence-closure.md` requirements 2-6; and the Standards
and Spec evidence in Ralph review runs `2026-07-19_192334_architecture_review` and
`2026-07-19_193824_architecture_review`.

## Acceptance Criteria
- Convert the retained checksum-drift, stale-initiation, historical-SAP-migration, and private-
  fixture review probes into permanent public-seam regression tests that fail before the fix.
- When canonical post-transfer evidence is invalid, the public account list returns exactly
  `total_count=0` and no rows, detail returns 404, and related actions/mutations cannot operate.
- Loan Account, S36, S37, combined Senior Finance, and CFC collection counts, pages, rows, details,
  available actions, and mutations consume one exact owner decision; no projector may silently
  drop an identity after it was counted.
- Senior Finance scope requires the exact current assignment/read authority, CFC scope requires
  the exact current task/authority, and an initiation permission never widens public read scope.
- Coherent SAP completions that predate the checksum field remain visible after migration, while
  missing, mismatched, or tampered delivery evidence remains fail-closed; migration behavior is
  tested from the historical state to the current leaf state.
- Replace the runtime Epic 009 fixture's `TestCase`, `setUp`, test-module, and private-helper
  dependencies with reusable public fixture/domain builders.
- Execute the actual fresh-database union of all E2E seed families and prove it is idempotent and
  order-safe without duplicate `DocumentTemplate` or destructive reseeding failures.
- Add bounded table-driven 1/21/101, more-than-four-adjacent-invalid, first/middle/last/out-of-range
  page, scalar-drift, paired action/mutation, query-ceiling, and independent 400/403/404/409 checks
  for all five collection branches, reusing shared scenario builders to control suite cost.
- The six-test Epic 009 PostgreSQL acceptance label runs twice, the existing nine-state browser
  contract runs twice with valid distinct manifests, and all configured backend/frontend gates
  pass without weakening permissions, integrity checks, business rules, or evidence requirements.
