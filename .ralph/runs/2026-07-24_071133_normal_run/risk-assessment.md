# Risk Assessment

Risk level: Medium

- Selected slice: 012D-audit-explorer
- Mode: normal_run
- Manual review required: yes; independent Ralph validation is required before commit.

## Security and privacy

- Audit payloads may contain legacy raw PAN, Aadhaar, bank/BO account, cheque, credential,
  authorization, token, or request-body values. The shared recursive projector now redacts these
  key families before every explorer or audit-export serialization. Public API tests use raw fake
  values and prove they are absent.
- Broad report/management access could accidentally imply audit access. Each endpoint retains its
  distinct audit permission; an Internal Auditor additionally requires the active persisted
  `audit_readonly` grant. Other permission holders receive only actor-attributable or canonical
  loan/application-scoped rows.
- Export could bypass the explorer. `audit-log-export` remains reachable only through the 012C job
  route, requires `reports.export`, `audit.audit_log.read`, and the separately ungranted
  `audit.export`, and consumes the already-sanitised selector. The direct report route remains
  forbidden.
- IP and captured user-agent are returned only after audit endpoint and object-scope authority.

## Data and performance

- No model or migration changed; the existing append-only stores remain the only source of truth.
- Date filters use indexed timestamp range predicates rather than a date transform. Canonical
  entity/action/timestamp fields retain their existing indexes; references are bounded subqueries.
- Actor rows use `select_related`; the representative 40-row page asserts no more than eight SQL
  queries and stable newest-first UUID tie-breaking. JSON role-snapshot filtering relies on the
  retained JSON field; no speculative index migration was added without PostgreSQL plan evidence.

## Compatibility and verification

- Existing audit, workflow, and version list contracts were extended additively; their focused
  suites were updated and pass.
- Critical recorder, sensitive reveal, restricted document download, report export, and report
  catalogue reverse consumers pass.
- Django system and migration-sync checks pass. No frontend files or dependencies changed, so
  frontend gates are not impacted.
- The agent did not run the complete backend suite or coverage lane. The orchestrator owns the
  authoritative impacted/full lane and commit decision.
