# Execution Plan

Selected slice: 010K3-servicing-as-of-owner-boundary-closure

## Public seam

Keep the existing monitoring HTTP/module interfaces as the test surface. Deepen the loan-owned DPD
source decision, the communications dispatch preflight, and the quarterly MIS snapshot owner so
callers do not reconstruct private live state.

## Red/green sequence

1. Convert the three retained review probes into stable permanent tests backed by public servicing
   builders. Run their exact selectors RED and retain the output.
2. Add the single allowed migration and model guards that make current-DPD ownership bidirectional
   and approved operational policy versions immutable across instance/queryset/bulk/direct SQL and
   delete paths. Run the DPD owner tests GREEN.
3. Extend the loan-owned DPD source decision to consume retained capitalisation schedule evidence
   alongside repayment/reversal evidence, preserving transaction-date as-of behavior. Run the
   capitalisation and timing matrix GREEN.
4. Move reminder serviceability into the final communications provider preflight through a public
   callback/facade, expose bounded batch continuation and per-identity results, and test adverse
   repayment/scope/recipient/template races plus exact retry.
5. Reauthorize every MIS replay through current report scope and exact submitted-CFO authority;
   freeze source rows by owner-observed cutoff time so late writes/live changes cannot leak. Test
   exact/changed-key and source-write races.
6. Add the exact five-test `ServicingAsOfOwnerBoundaryPostgreSQLAcceptanceTests` class using stable
   builders. Run the declared class twice when PostgreSQL is available; otherwise retain the local
   socket limitation and rely on the independent trusted gate.
7. Run focused reverse-consumer tests, `manage.py check`, migration sync, and the exact closure
   validator. Save review-closure evidence, risk assessment, review packet, and final summary.

## Constraints

- One migration maximum; no frontend work, new policy, or private cross-`TestCase.setUp()` fixtures.
- Do not run the complete backend suite or coverage; independent validation owns those gates.
- Preserve the carried deep-ledger pagination debt outside this slice.
