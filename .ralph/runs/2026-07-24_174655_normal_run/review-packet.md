# Review Packet: 2026-07-24_174655_normal_run

## Result
Ready for independent validation

## Slice
012F-security-privacy-regression-checks

## Candidate

- Adds `manage.py security_regression --output <json>`.
- Freezes all 55 source controls (`SEC-AUTH-001..010`, `SEC-AUTHZ-001..007`,
  `SEC-PII-001..012`, `SEC-WEB-001..010`, and `AUD-001..016`) to real public behavior tests or an
  exact blocking finding.
- Adds deterministic summary counts, skips/reasons, scanner versions, redacted scanner reports and
  hashes, hardening checks, complete control evidence, and a canonical summary hash.
- Adds production security settings and separate production JWT signing-key enforcement.
- Pins required external scanner versions in lane policy and uses the existing npm lockfile,
  without adding packages outside the dependency allowlist.

## Standards Review

No candidate defect found. The implementation uses the existing Django management-command,
settings, auth-token, public API test, and evidence patterns. It adds no schema, business API,
frontend, protected-path, or source-document changes. New behavior tests exercise public
interfaces; scanner/process seams are injected only at the external subprocess boundary.

## Spec Review

The slice boundary is implemented without a second auth/encryption/audit subsystem. Mandatory
missing controls and scanners fail visibly. The real result is intentionally not a false green:
52 controls pass, three exact product controls fail, two Python scanners are not installed in the
agent environment, and npm advisory lookup is unavailable. Those failures are retained in the
summary and risk assessment.

## Traceability

- The source says authentication, authorisation, sensitive-data, web, and audit controls must be
  release-tested (`docs/source/test-plan.md` §18); the code maps every listed ID in
  `security_regression/matrix.py`, verified by
  `test_control_matrix_contains_every_source_control_exactly_once` and
  `test_every_matrix_test_label_resolves_to_a_real_behavior_test`.
- The source says production must disable debug, enforce HTTPS/secure cookies/HSTS, restrict
  hosts/origins, and separate secrets (`docs/source/security-privacy.md` §§15, 18, 30 and
  `docs/source/technical-architecture.md` §32); production settings do so, verified by
  `ProductionSettingsSecurityTests` plus existing demo-isolation and field-key tests.
- The source says secret and dependency scans are required and missing scanners cannot be silent
  (`docs/source/security-privacy.md` §29 and `docs/source/deployment-ops.md` §11); the command makes
  every scanner mandatory and redacts raw output, verified by
  `test_required_scanner_unavailability_and_findings_fail_without_raw_output`.
- The source says the summary must fail non-zero and identify an exact control; the controlled
  failure demo exits 1 for `SEC-AUTH-001` and writes only that failing control.

## Validation Evidence

- Consolidated TDD evidence: `evidence/terminal-logs/tdd-red.log` and
  `evidence/terminal-logs/tdd-green.log`.
- Consolidated focused validation: 59 auth/security/reverse-consumer tests passed; Django system
  check and migration sync passed; command/scanner/no-secret outputs are retained in
  `evidence/terminal-logs/validation.log`.
- Real lane summary and full matrix: `evidence/security-regression-summary.json`.
- Controlled failure: `evidence/controlled-failure-summary.json` and its terminal log.
- npm report plus its network failure are retained in `evidence/npm-audit-report.json` and the
  consolidated validation log.
- The evidence secret scan recorded zero matches in the consolidated validation log.
- The authoritative complete backend coverage lane is intentionally left to the orchestrator.

## Blocking Findings

| Finding | Control | Disposition |
|---|---|---|
| `SECURITY-012F-LOGIN-RATE-LIMIT` | `SEC-AUTH-010` | Release blocker; route through a prepared corrective slice. |
| `SECURITY-012F-UPLOAD-FILENAME` | `SEC-WEB-004` | Release blocker; route through a prepared corrective slice. |
| `SECURITY-012F-UPLOAD-CONTENT` | `SEC-WEB-005` | Release blocker; route through a prepared corrective slice. |

## Recommended Next Action
Run independent High-risk validation after provisioning the exact lane-pinned scanner versions.
Keep the three product findings release-blocking and prepare corrective slices through the normal
owner/architecture workflow; do not reinterpret scanner unavailability as a skip.
