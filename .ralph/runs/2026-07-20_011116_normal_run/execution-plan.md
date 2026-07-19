# Execution Plan

Selected slice: `010C2-manual-allocation-and-financial-reversal-controls`

## Boundary

Implement only the backend/API financial correction boundary declared by 010C2: harden ordinary
allocation admission and idempotency, add approved exception allocation and append-only reversal,
reconcile source-backed role grants, and retain immutable/sanitised decision evidence. No frontend,
refund, write-off, charge-ordering, cash, or generic ledger-editing work is in scope.

## Public behaviours and TDD order

1. Add one public API regression test proving allocation is zero-write until the receipt has a
   retained posted SAP decision and an exact bounded `Idempotency-Key`; make it RED, implement the
   canonical admission/idempotency seam, then save GREEN evidence.
2. Add schedule reconciliation tests proving the account, allocation, ledger, and 1/21/101-row
   schedule truth reconcile exactly and insufficient/empty capacity fails closed; implement the
   schedule application behind the allocation owner.
3. Add public manual-allocation tests for one unresolved 010D exception with terminal exact
   approval, including missing/pending/foreign/drift/replay denials; implement the approval evidence
   and action while delegating the financial transition to the canonical allocator.
4. Add public reversal tests proving one authorised action appends compensating allocation/ledger
   truth, restores schedule/account balances, preserves originals, and rejects stale/foreign/
   duplicate/changed replay attempts; implement the narrow elevated permission without default role
   grants.
5. Add the four-test PostgreSQL acceptance label for allocation/reversal races and retain twice-run
   evidence when the local PostgreSQL capability is available.

## Expected edits

- `sfpcl_credit/loans/`: models, one non-destructive migration, allocation/correction module,
  serializers/views/routes, and focused public tests.
- `sfpcl_credit/identity/`: source-backed default permission catalogue/grants only.
- `docs/working/API_CONTRACTS.md`: exact allocation/manual-allocation/reversal contracts and errors.
- Current run evidence: RED/GREEN logs, API/permission/ledger proof, finding closure evidence,
  risk assessment, review packet, and final summary.

## Validation

- Use `/Users/amitkallapa/LMS/.ralph/venv/bin/python` for every backend command.
- Run each focused RED/GREEN cycle and impacted 010A-010D reverse-consumer tests.
- Run `manage.py check` and `makemigrations --check`; do not run the complete backend suite or full
  coverage because the orchestrator owns those authoritative gates.
- Confirm diff limits/protected paths, then set review result exactly to
  `Ready for independent validation`.
