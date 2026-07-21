# Review Packet: 2026-07-21_091246_normal_run

## Result
Ready for independent validation

## Slice
010L-member-portal-repayment-view

## Recommended Next Action
Run Ralph's independent High-risk backend coverage and trusted browser contract twice, then commit
and merge only if every gate passes.

## Outcome

MP15-MP18 now consume a separate borrower-safe servicing API rather than staff serializers or
runtime fixtures. The API derives ownership from the active portal principal, exposes bounded
account/schedule/confirmed-repayment/issued-invoice data, and returns masked direct instructions
only when explicitly approved. The portal parent retains the exact account selected in My Loans;
Repayments and Direct Repayment never rank or choose an account in the browser.

## Traceability

- The source says MP15 lists own active/closed accounts and opens MP16
  (`screen-spec-member-portal.md` MP15); the code exposes and renders own-member list/detail facts,
  verified by `PortalLoanAccountsApiTests.test_owner_list_detail_and_nested_reads_project_only_borrower_safe_truth`
  and the explicit-selection frontend test.
- The source says MP17 shows payments only after SFPCL confirmation, with principal/interest split
  (`screen-spec-member-portal.md` MP17); the code requires posted canonical allocation truth and
  excludes a pending receipt, verified by the same backend test and `PortalLoanViews.test.tsx`.
- The source says MP18 displays only approved repayment details, required narration, due amount, and
  a verification disclaimer (`screen-spec-member-portal.md` MP18); the code masks last four, disables
  proof submission, and fails closed without approved configuration, verified by
  `test_direct_instructions_are_masked_read_only_and_server_owned`.
- Auth §§19.3/20.2 require borrower-self scope; actual foreign and guessed account/nested routes,
  caller member claims, staff tokens, and suspended portal accounts are verified by
  `test_foreign_guessed_staff_claimed_member_and_inactive_portal_are_nondisclosing`.

## Review notes

- No production model or migration was added. The projection reuses existing canonical loan,
  schedule, allocation, repayment, and invoice owners.
- No staff endpoint/serializer is exposed to portal callers, and response examples contain no actor,
  SAP, provider, audit, raw bank, remarks, or exception fields.
- A-151 records the fail-closed repayment-instruction governance seam. This implementation does not
  broaden the unresolved borrower proof/UTR policy.
- Diff remains within Ralph limits and no protected, forbidden, source, orchestrator-owned state,
  progress, selected-slice status, or handoff file was changed.

## Evidence

- RED: `evidence/terminal-logs/portal-loan-accounts-red.log`
- GREEN: `evidence/terminal-logs/portal-loan-accounts-green.log`
- Focused backend: `evidence/terminal-logs/backend-focused-regressions.log`
- Frontend complete suite/build/typecheck/lint: `evidence/terminal-logs/frontend-tests.log`,
  `frontend-build.log`, `frontend-typecheck.log`, `frontend-lint.log`
- Browser collection/local infrastructure outcome: `evidence/terminal-logs/browser-contract-collection.log`,
  `browser-acceptance-local.log`
- Safe response and mock-removal proof: `evidence/safe-response-examples.md`,
  `evidence/terminal-logs/mock-removal-proof.log`

## Independent review focus

1. Confirm canonical `RepaymentAllocation` terminal/reversal filtering remains consistent with the
   financial owner's semantics under the complete suite.
2. Confirm the trusted browser run produces all four exact screenshot names and that the long MP17
   table remains usable at 390px while MP18 remains read-only.
3. Confirm deployment governance leaves repayment instructions unavailable until the collection
   account is separately approved and provisioned.
