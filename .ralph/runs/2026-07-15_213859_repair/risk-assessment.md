# Risk Assessment

Risk level: High (slice declaration)

- Selected slice: CR-008-document-template-constraint-migration-nondeterminism
- Mode: repair
- Standing approval: active; no owner veto is recorded.

## Material Risks

- The forward migration removes and recreates two database check constraints. Django migrations are
  atomic on the production PostgreSQL target, so other sessions do not observe a committed
  unconstrained intermediate state, but adding the constraints may take a schema lock and scan the
  document-template table during deployment.
- A mistaken value/order/name could change runtime database enforcement. The regression asserts the
  exact three approval statuses, nullable three borrower variants, both existing names, terminal
  migration state, allowed inserts, and rejection of values outside each catalogue.
- Rewriting historical migration `0002` would make applied history unsafe. It remains unchanged;
  the repair is isolated in forward migration `0005`.

## Reduced Blast Radius

- No data migration, column, index, endpoint, service, permission, role, frontend, dependency, or
  source-document change.
- Template selection/generation behavior and the class-level validation catalogues are unchanged.
- Full backend and frontend gates passed, including migration drift across five hash-seed settings.

Residual risk is deployment-time schema-lock duration on an unusually large template table. The
table is a small administrative catalogue, and the migration neither transforms rows nor weakens
the final constraints.
