# Risk Assessment

Risk level: High

- Selected slice: 012D2-auditor-observation-workflow
- Mode: normal_run
- Manual review required: yes; independent Ralph validation is required before commit.

## Primary risks and controls

- **Authority expansion:** New create/read permissions are dedicated to observations, granted only
  to Internal Auditor, and additionally require the active persisted `audit_readonly` scope.
  Copying the permission codes to an operational role still denies.
- **Operational or audit-truth mutation:** Observation writes are isolated in their own model and
  service. No source owner is called for mutation. Observation HTTP and ORM mutation paths reject.
- **Sensitive evidence disclosure:** Compliance evidence is resolved under compliance read
  authority. File bytes additionally require current document-download authority and a short-lived
  capability bound to user, scope, observation, evidence, and document. Safe projections omit
  summaries, review comments, source payloads, checksums, and storage locations.
- **Forged or stale references:** One to 20 distinct UUID references are resolved server-side
  against a supported immutable owner. Missing, wrong-family, revoked, guessed, or cross-observation
  access is nondisclosing and audited.
- **Stored injection or personal data:** Observation text uses the existing audit-text guard plus
  active-content and PAN-like rejection. Unsafe input is not echoed or retained.
- **Schema risk:** One additive migration creates one table, one index, one check constraint, and
  protected creator linkage. There is no destructive data migration.
- **Compatibility risk:** The Internal Auditor's general no-operational-create regression now names
  the one observation-only exception. The remaining 83 audit, 011O, configuration, document,
  catalogue, and sanitisation tests pass unchanged.

## Remaining independent checks

The agent ran focused checks and reverse consumers only, as required. Ralph must run the
authoritative High-risk complete backend coverage lane, migration consistency, protected-path,
artifact, and diff-limit validation before commit.
