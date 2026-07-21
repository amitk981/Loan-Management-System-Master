# Impact Analysis

Selected slice: `CR-015-epic-010-terminal-servicing-owner-finalizer`

## Affected backend modules

- `monitoring`: reminder delivery claims/serviceability and immutable quarterly-MIS cutoff decisions.
- `communications`: the generic dispatch seam used by reminder delivery, limited to accepting and
  enforcing the final owner decision without changing unrelated communication flows.
- `loans` / `processes`: one composite direct-repayment command that owns capture, SAP posting,
  allocation, replay, and retained completion; concurrent statement generation ownership and the
  borrower-safe statement projection.
- `members` / portal servicing process: complete or explicit pagination of borrower collections and
  backend-owned, versioned direct-repayment instruction/action projections.
- Models/migrations only where durable claim, step-state, cutoff-decision, or projection provenance
  cannot be represented by existing retained records. PostgreSQL locking and unique constraints are
  required for financial and artifact idempotency.

## Affected frontend modules

- `sfpcl-lms/src/services/servicingApi.ts`: replace the browser-owned capture/SAP/allocation
  coordinator with one backend command.
- `sfpcl-lms/src/pages/repayments/RepaymentsHub.tsx`: consume only the composite command's retained
  complete outcome and never render partial capture as completion.
- `sfpcl-lms/src/services/portalApi.ts` and existing portal loan views: traverse canonical
  pagination or expose truthful continuation; consume backend-owned instructions/actions.
- Existing styling and page structure remain unchanged under `FRONTEND_DESIGN_RULES.md`.

## Blast radius

- High financial/data-integrity risk: repayment retries and concurrency can affect balances,
  allocations, ledger rows, SAP evidence, and the response reported to staff.
- High external-side-effect risk: reminder checks and provider calls must have one final server
  owner across repayment, scope/source changes, cancellation, timeouts, and competing workers.
- Historical-reporting risk: post-cutoff invoice, repayment/reversal, reminder, DPD, disbursement,
  capitalisation, and account transitions must not mutate a generated quarter-end view.
- Privacy risk: borrower CSV and portal projections must not expose internal owner identifiers,
  staff names, SAP state, remarks, or silently truncated collections.
- Concurrency risk: equal-key statement requests and direct-repayment commands must converge to one
  retained artifact/effect under PostgreSQL.
- Reverse consumers to protect: existing reminder jobs, communication retries, MIS submit/review and
  exports, repayment capture/allocation APIs, staff account/repayment UI, and member portal views.

## Regression tests to add

- `monitoring`: permanent public-seam reminder races covering repayment-after-check, scope/source
  change, competing workers, exact retry, and provider timeout; 1/100/101 reminder batches.
- `monitoring`: before/cutoff/after matrices for every mutable MIS input plus immutable exact replay.
- `loans/processes`: composite command crash-boundary replay after capture, SAP decision, allocation,
  and response retention; changed-key/cross-account conflicts and concurrent exact-key execution.
- `processes`: concurrent statement replay produces one artifact; borrower CSV safe-field and empty
  metadata cases.
- `portal`: 1/100/101 schedule/repayment/invoice collections and approved/versioned instruction and
  action projections.
- `frontend`: servicing transport calls one composite endpoint; repayment UI accepts only complete
  retained outcomes; portal transport/view behavior cannot silently stop at the first 100 rows.
- `sfpcl_credit.tests.test_epic010_terminal_owner_finalizer`: exactly five PostgreSQL acceptance
  tests, executed twice, covering the slice's declared race contract.

## Scope controls

- No new allocation, reminder cadence/content, MIS column, statement layout, portal styling,
  interest, default, or scheduler policy.
- Consume the existing DPD owner decision and existing allocation/SAP owners through public seams.
- Replace cross-`TestCase.setUp` fixture borrowing with public builders only in touched acceptance
  classes.
