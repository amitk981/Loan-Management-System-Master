# Execution Plan

Selected slice: 009H3A-communications-advice-persistence-and-provider-identity

1. Preserve the current 009H2 public interface while moving only canonical persistence and adapter
   identity into communications. Keep `DisbursementAdviceIntent` in disbursements and expose the
   transferred receipt through a shallow compatibility alias with no manager, query, rendering,
   delivery, receipt, or audit policy.
2. TDD tracer bullet: add a public model-ownership test that initially fails because the outbox is
   absent and the retained receipt still belongs to disbursements. Implement only the canonical
   communications models needed to make this behavior green.
3. Add a migration-executor test that starts at the exact pre-009H3A leaves, creates a genuine sent
   receipt, records row ids and table/constraint signature, migrates forward, reverses, and reapplies.
   Implement one communications migration using `SeparateDatabaseAndState`: create exactly one
   outbox table and transfer receipt state without receipt-table database operations or data rewrite.
4. Add one shared Manual/Fake/Future adapter contract test at a time for stable-key identity under
   payload mutation, fresh-instance replay, provider rejection/retry, and replaceability. Make the
   minimum adapter changes per red→green cycle; retain strict result validation and no network I/O.
5. Add import/compatibility tests proving canonical class identity, shallow legacy aliases, and no
   communications-to-disbursements policy/model import cycle. Run focused retained 009H2 success,
   replay, rejection, permission, audit/workflow, receipt, and no-financial-side-effect regressions.
6. Save red/green output, a receipt schema/row manifest, migration plan and sync output, adapter
   contract output, and an import graph under this run's evidence directory. Run Django check and
   focused backend tests with `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; do not run the full
   backend suite locally.
7. Review the diff against the 30-file, 2,000-line, one-migration limits and protected-path rules.
   Update the current slice, state, progress, handoff, digest, changed-files, risk assessment,
   review packet, and final summary. Recheck and sharpen the next one or two Not Started slices only
   from the already-opened Epic 009 material, then leave commit/merge/push to the orchestrator.
