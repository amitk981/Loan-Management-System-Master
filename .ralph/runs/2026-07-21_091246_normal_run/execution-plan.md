# Execution Plan

Selected slice: 010L-member-portal-repayment-view

1. Add focused failing Django API tests for portal-principal-only loan list/detail access, bounded schedule/repayment/invoice projections, verified-posted repayment filtering, approved masked direct instructions, foreign-object nondisclosure, and staff/locked/missing portal denial. Save the RED output.
2. Implement a borrower-safe portal servicing projection behind the existing portal authentication boundary, expose separate `/api/v1/portal/loan-accounts/` list/detail and nested read routes, and reuse canonical loan/interest models without staff serializers or caller-supplied member identity. Save the GREEN output and safe response examples.
3. Add frontend service contracts and focused component tests for exact URLs, populated/empty/loading/error/unauthorised states, explicit account selection, posted repayment truth, and read-only direct instructions; prove the four screens contain no runtime mock or inline business fixtures.
4. Wire MP15–MP18 and the borrower portal route using only existing portal/table/card/badge patterns. Keep proof/UTR submission and browser-side financial calculations disabled. Add the declared Playwright acceptance spec and screenshot assertions for populated, empty, error, and mobile states.
5. Update the repository API contract and prototype inventory/gap ledger for the new borrower-safe projection and MP16 screen.
6. Run focused backend and portal regressions, frontend focused tests, typecheck, lint, build, Django check, and migration sync. Do not run the complete backend suite; independent Ralph validation owns it for this High-risk slice.
7. Save terminal logs, mock-removal and response evidence, risk assessment, review packet, and final summary. Confirm diff limits and set the review result exactly to `Ready for independent validation`.
