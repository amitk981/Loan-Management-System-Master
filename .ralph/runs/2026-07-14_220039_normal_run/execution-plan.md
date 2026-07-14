# Execution Plan

Selected slice: `008H-sh-4-physical-share-security-workflow`

## Scope and interface

- Extend the retained `security_instruments.SecurityPackage` module with exactly one protected
  `SH4ShareTransferForm` per package and the source §28.4 POST/GET/PATCH routes.
- Accept exactly `member_id`, `witness_id`, `shareholding_id`, nullable `share_count`,
  `loan_document_id`, `form_status`, `custody_location`, and `signed_at`. Keep invocation and return
  facts database-null and reject those lifecycle states.
- Refresh only the package's physical/demat requirement flags from the canonical frozen sanction
  share mode; keep missing/mixed modes blocked and preserve PoA, status, loan-account, cheque, and
  readiness facts.
- Consume current SH-4 renderer, exact borrower/witness signatures, and adequate stamp evidence
  only through `legal_documents` selectors. Retain Compliance preparation/current-maker identity;
  allow only a distinct Company Secretary to record terminal custody and return the durable §6.3
  action identity.
- Project document/signature/custody metadata into package and checklist reads without completing,
  approving, invoking, returning, downloading, or making the package/disbursement ready.

## TDD tracer bullets

1. Add one public HTTP test for physical package refresh plus Compliance pending SH-4 create/read,
   exact replay, strict request shape, one-current-row uniqueness, retained evidence, and unchanged
   checklist/package/PoA truth. Save the failing output, implement the model/request/module/routes,
   then save green output.
2. Add one public HTTP test for signed/custody validation across canonical borrower, current verified
   shareholder witness, active physical shareholding/share count, current renderer, exact signatures,
   adequate non-legacy maker/checker stamp, and distinct Company Secretary custody. Save red/green
   evidence and add upstream consumed-evidence protection.
3. Add focused denial/projection tests for demat/mixed/missing mode, inactive/nonphysical/wrong-owner
   shareholding, wrong/cross-application witness/document evidence, legacy/null makers, role and
   permission ordering, forbidden invoked/returned states, projection rollback, and zero success
   evidence on denial. Save red/green evidence.
4. Add PostgreSQL five-worker create and changed-custody/downgrade races, each asserting one retained
   current row, winner/loser outcomes, and attributable audit/version/workflow identity. Run each
   race twice when the declared PostgreSQL harness is available.

## Documentation and completion

- Generate one migration and verify model/migration sync.
- Update `docs/working/API_CONTRACTS.md` with the exact §28.4 contract and update the Epic 008 digest
  only with durable implementation facts learned in this run.
- Run focused backend tests with the mandated interpreter, then Django check, migration sync, full
  backend coverage, and frontend build/typecheck/lint/tests. Save command output under
  `evidence/terminal-logs/` and API response examples under the run folder.
- Sharpen the next eligible Not Started slice(s) only from source material already opened, then
  update the selected slice status/checklist, `.ralph/state.json`, `.ralph/progress.md`, and
  `docs/working/HANDOFF.md`.
- Produce `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`, and
  verify protected paths, diff limits (30 files / 2,000 lines), and the absence of frontend changes.

## Risk controls

- High risk: critical security custody, maker-checker identity, document/signature evidence,
  permissions, immutable audit history, and concurrency.
- No file/download authority is introduced. No nominal stamp amount is hard-coded. No invocation,
  return, share reservation/decrement, package completion, or readiness rule is implemented.
- Every mutation stays inside the package transaction/lock; projection failure rolls back the row
  and every success ledger. Exact replay is zero-write and never transfers maker/custodian identity.
