# Standards Review

Fixed product boundaries: `399fb954..50d91369` (009L6) and
`d17954b8..fe4b0ecb` (CR-012). Ralph infrastructure and mechanical bookkeeping
were excluded.

1. **High — hard violation:** `loan_account_read.py:28-61` lets
   `finance.disbursement.initiate` substitute for `finance.loan_account.read` and grants Senior
   Finance the full Loan Account portfolio. `loan_account_360.py:124-145` does not reapply object
   scope for lists although detail reads do. This contradicts `API_CONTRACTS.md` Loan Account and
   payment-initiation scope, auth §34.7, and codebase-design §42.2 permission enforcement.
2. **High — hard violation:** `sap_customer_profile.py:393-424,628-659` still implements SQL
   selector subsets beside stricter scalar validation at lines 700-813. Selectors self-compare
   stored JSON but omit relations and actual workbook integrity checked by the scalar owner.
   `current_disbursement_evidence.py:83-203` similarly omits scalar owner facts enforced later.
   This repeats the boundary defect prohibited by the 009L6 API contract and codebase-design
   §§26.2/42.1-2.
3. **Medium — hard architecture drift:** `seed_epic_009_e2e_fixture.py:101-163` imports a test
   `TestCase`, calls `setUp`, and relies on private fixture helpers instead of public owner
   interfaces, contrary to codebase-design §§26.1-2/42.1.
4. **Medium — hard regression:** `playwright.config.ts:31-44` seeds Epic 009 only when its filename
   appears in argv while global `testMatch` always includes it. Ordinary `npm run e2e` therefore
   collects the spec without its required seed.
5. **Low — judgment call:** JSON selector helpers are triplicated across lifecycle, SAP, and
   disbursement modules; tests also instantiate other `TestCase` classes and private helpers.
   Assertions are real, but seam fidelity and locality remain weak under codebase-design §§26/42.

No production frontend styling drift was found.
