# Risk Assessment

## Classification

High, as declared by slice 012A3. The change exposes compliance/default/recovery/closure report
reads and defines the restricted audit-export handoff. There are no models, migrations,
dependencies, frontend changes, writes, export files/jobs, or external side effects.

## Principal risks and controls

- Cross-scope disclosure: every selector requires the exact owning read permission and reuses the
  owner's persisted case/account/member/application/audit scope.
- Sensitive disclosure: recovery evidence, KYC identifiers/documents, stamp evidence, restricted
  legal/Board documents, grievance internals, and closure document/storage authority are omitted.
- Reconciliation drift: selectors delegate to owner interfaces/serializers or query owner records
  only after the same canonical scope. Focused reverse-consumer tests remained green.
- Incorrect totals/pagination: totals use the complete filtered scope before pagination; ordering
  ends in immutable UUID identity.
- Audit export bypass: the registry entry is metadata-only (`selector=None`); generic report
  access always denies, including with all current audit/export permissions.
- Recursive read auditing: report reads create no row-level audit events. 012C remains responsible
  for export request/download auditing.

## Residual risk

The orchestrator must run the authoritative High-risk complete backend coverage lane and validate
the configured 85% floor. Export policy/jobs and the audit explorer remain owned by 012C/012D.

## Gate evidence

- 19 focused report tests: pass.
- 95 focused owner/reverse-consumer tests: pass, one pre-existing skip.
- Django system check: pass.
- Migration consistency: pass, no changes detected.
- `git diff --check`: pass.
