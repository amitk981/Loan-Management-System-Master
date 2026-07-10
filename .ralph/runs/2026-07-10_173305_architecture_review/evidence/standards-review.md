# Standards

- **Hard:** `credit/modules/appraisal_workflow.py` stores only mutable assessment UUIDs while
  `loan_limit_calculator.py` replaces current facts under the same UUID. API §3 requires decision
  snapshots. Appraisal PATCH can therefore be reinterpreted by a later rerun. ADR-0003 and 006E2
  own the correction without changing accepted assessment-rerun behavior.
- **Hard:** submit-for-review validates required `remarks` but discards them. API §3 requires a
  sensitive action's reason to be captured. 006E2 persists the reason outside metadata-only audit
  JSON and tests rollback/redaction.
- **Hard test gap:** the financial locking test mocks managers and asserts
  `select_for_update.called`; it does not exercise competing transactions as required by
  codebase-design §26.3. 006D2C adds an independent-connection outcome regression.
- **Medium:** the AST boundary checks only one concrete-model import form, allow a package-level
  alias bypass, and use `issubset` where a required public import can be absent. The exact full
  `AppraisalWorkflow` method-set assertion is also brittle under §§26.1-26.2. 006D2C owns robust
  positive/negative fixtures.
- **Judgment/watch:** source §14.3 expresses a normal application FK and nullable appraisal risk FK,
  while 006E enforces one required risk per application/appraisal. No reviewed workflow requires
  concurrent risk versions, so this is recorded as drift to watch rather than corrective work.

Worst Standards issue: an appraisal cannot preserve its financial decision basis after a
same-UUID assessment rerun. Four actionable findings; one watch.
