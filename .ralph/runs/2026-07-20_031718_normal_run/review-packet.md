# Review Packet: 2026-07-20_031718_normal_run

## Result
Ready for independent validation

## Slice
010E-subsidiary-deduction-reconciliation

## Recommended Next Action
Run the orchestrator-owned PostgreSQL acceptance, complete backend coverage, migration-sync,
protected-path, and candidate-size gates; integrate only if all pass.

## Delivered behavior

- The shared repayment endpoint now captures source-defined subsidiary deduction fields only when a
  current executed/verified/render-valid tri-party agreement exists. It supports exact replay and
  an optional exact 010D-owned statement-line claim.
- Subsidiary/agreement/reference evidence, 010D statement truth, Treasury decision, SAP obligation,
  SAP posting, 010C allocation, and ledger movement remain separate. A new Treasury verification
  action requires a coherent exact or authorised statement match and records excess as a nonposting,
  nonallocating exception.
- Subsidiary SAP posting is blocked before Treasury verification; exact terminal replay is
  zero-write. 010C now rejects subsidiary allocation unless statement, reconciliation, and Treasury
  evidence are coherent, while retaining all existing principal-first logic.
- One migration adds database-backed subsidiary evidence, reference uniqueness, bounded status, and
  Treasury evidence-coherence constraints. A-144 documents the missing company-registry owner.

## Source traceability

- The source says subsidiary repayment captures subsidiary, produce/payment, transfer, amount/date,
  and bank facts and blocks duplicate references (`product-requirements.md` §11.23; API §32.3/§45).
  The code validates and normalizes those facts in
  `loans.modules.subsidiary_deduction_reconciliation`; verified by
  `test_verified_agreement_allows_subsidiary_deduction_capture`,
  `test_capture_validation_agreement_duplicates_and_replay_are_zero_balance_write`, and
  `test_capture_can_claim_one_preexisting_exact_statement_through_010d_owner`.
- The source says a tri-party agreement must exist, borrower name plus application number are both
  required for automatic matching, unclear deductions go to reconciliation, and Treasury precedes
  SAP (`user-flows.md` §28; BR-058/059; M09-FR-006/007). The code consumes the legal selector and
  010D relationship owner before Treasury/SAP; verified by
  `test_exact_statement_treasury_sap_and_canonical_allocation_complete_in_order` and
  `test_unclear_statement_and_excess_amount_remain_nonallocating_exceptions`.
- The source says outstanding changes only after posting and partial repayment is principal-first
  (`functional-spec.md` §11.9/M09-FR-004/010). The subsidiary module delegates to 010C and contains no
  balance/ledger calculation; verified by the ordered E2E test plus the retained 010C reverse-
  consumer suite.
- The source role table authorises Credit Manager/Accounts mutation and requires audit truth
  (`auth-permissions.md` §26.6; security §§22.2/23.1). The module enforces effective role, permission,
  and scope and hashes sensitive reference/reason text in audit; verified by
  `test_effective_role_permission_and_nondisclosing_scope_guard_every_mutation` and the capture audit
  assertions.

## Evidence reviewed

- RED tracer: `evidence/terminal-logs/subsidiary-tracer-red.log`
- GREEN tracer: `evidence/terminal-logs/subsidiary-tracer-green.log`
- RED/GREEN ordered flow: `evidence/terminal-logs/subsidiary-e2e-red.log` and
  `evidence/terminal-logs/subsidiary-e2e-green.log`
- Six-test subsidiary matrix: `evidence/terminal-logs/subsidiary-api-matrix.log`
- Reverse consumers: `evidence/terminal-logs/direct-repayment-reverse-consumer.log`,
  `evidence/terminal-logs/allocation-reverse-consumer.log`, and
  `evidence/terminal-logs/statement-matching-reverse-consumer.log`
- PostgreSQL label collection: `evidence/terminal-logs/subsidiary-postgresql-collection.log`
- Check/migration/lint/compile gates: `evidence/terminal-logs/backend-static-gates.log`

## Reviewer focus

- Execute both PostgreSQL race tests and confirm statuses/evidence counts under real row locking.
- Confirm the optional statement-line capture path and post-import auto-match path retain the same
  010D relationship owner.
- Confirm A-144 is acceptable until a canonical subsidiary-company registry is scheduled.
