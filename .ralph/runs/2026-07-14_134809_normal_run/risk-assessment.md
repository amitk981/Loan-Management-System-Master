# Risk Assessment

Risk level: High (owner standing approval; no revocation)

The slice changes sanction finalisation, legal-document lifecycle ownership, audit semantics, and
object-scope enforcement. A defect could create an incomplete sanctioned package, destroy completion
evidence, misstate a legal audit delta, or disclose checklist existence.

Controls applied:

- public terminal approval cannot inject/bypass completion; missing coordination is zero-write;
- approval and application rows are locked and all completion side effects share one transaction;
- canonical frozen latest-cycle facts replace cached/shallow status authority;
- completion/verification/checklist/signature facts are preserved and conflicting correction rolls
  back the entire ledger;
- permission/object scope is resolved before legal checklist/item access;
- application and approval owners publish conditional facts through narrow seams;
- two genuine PostgreSQL five-worker final-sanction races passed;
- full backend/frontend gates and two independent review axes passed.

Residual risk: the underscored Python coordinator seam is conventional module privacy rather than a
language-enforced capability, and future internal callers must continue to enter through
`processes.sanction_completion`. Database uniqueness/locking and the public-interface regression
limit accidental bypass. Later 008D/008E work must use the sharpened narrow lifecycle/fact seams and
must not call broad applicability refresh for unrelated status changes.

No schema migration, dependency, external side effect, source edit, protected-file edit, or frontend
change occurred. The diff remains below Ralph file/line limits.
