# Risk Assessment

Risk level: High

- Selected slice: 011D-non-payment-note-workflow
- Mode: normal_run
- Manual review required: yes; independent Ralph validation remains authoritative.

## Risk drivers and mitigations

- Financial snapshot integrity: principal and interest are taken from the locked canonical loan
  account and caller values must match exactly. Non-finite, negative, stale, and forged values fail
  before writes. Submitted decision inputs are immutable except through an explicit returned cycle.
- Authorization and disclosure: create and submit require both the named permission/role and the
  existing object-scoped default-case selector. Note projection is limited to Credit Assessment,
  Credit Manager, active audit scope, and the retained configured approvers.
- Workflow and approval ownership: the recovery module creates one retained approval case from the
  effective committee snapshot but exposes no recovery decision actions. Slice 011E remains the
  owner of approve/reject recovery decisions. The existing approval owner performs the explicit
  return transition and records its immutable action/event trail.
- Concurrency: row locks, unique constraints, replay comparison, and retained case reuse make exact
  create/submit retries converge. The required two five-worker PostgreSQL tests are present and
  locally discovered; authoritative PostgreSQL execution is deferred to the orchestrator lane.
- Formal document retention: draft, submitted, and corrected versions are generated as restricted
  PDFs with checksums and document audit entries. The storage adapter deletes bytes when document
  persistence itself fails. A process/database failure after successful storage but before the
  enclosing transaction commits can leave an unreferenced local object; this matches the current
  storage transaction boundary and is a non-blocking operational cleanup risk, not a business-state
  integrity risk.
- Regression surface: approval selection/read/return behavior and permission catalogue mappings are
  shared infrastructure. The complete focused approval-routing file (129 tests), catalogue file (18
  tests), and prior default/grace/extension API files (24 tests) pass after the changes.

## Validation evidence

- `non-payment-workflow-final.log`: 6/6 workflow/API behaviors pass.
- `approval-routing-regression.log`: 129 run; 127 pass and 2 pre-existing skips.
- `catalogue-seed-regression.log`: 18/18 pass.
- `default-recovery-reverse-final.log`: 24/24 pass.
- `non-payment-postgresql-class-final-discovery.log`: exactly 2 tests found; both SQLite skips carry
  the required PostgreSQL marker.
- `backend-final-checks.log`: system check clean and no migration drift.
