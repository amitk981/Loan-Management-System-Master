# Risk Assessment

Risk level: High.

- This relocates regulated SAP request, delivery, customer-code, sensitive-workbook, permission,
  audit, and concurrency behavior across Django app ownership.
- No model, migration, table, route, success payload, permission, ciphertext context, retained row,
  or external integration was added or changed. Finance's model alias remains object-identical.
- Main regression risks are import cycles, stale private imports, replay drift, secret disclosure,
  and race behavior. AST graph tests, 58 public/downstream tests, safe-audit assertions, Django
  migration sync, and two PostgreSQL race runs mitigate them.
- The implementation is compact to remain below Ralph's 2,000-line move limit; the deep public
  interface and separated request/code/storage modules preserve navigability despite that constraint.
- The orchestrator must still run authoritative full coverage and configured frontend gates.
