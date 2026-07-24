# Auditor Observation Permission Matrix

| Actor/current authority | Create | List/detail | Restricted evidence bytes | Result |
|---|---:|---:|---:|---|
| Active Internal Auditor + active `audit_readonly` + observation create/read | Yes | Yes | No unless separately authorised | Governed observation access |
| Same auditor + `reports.compliance.read` | Yes | Yes | No | Evidence identity and safe metadata only |
| Same auditor + `reports.compliance.read` + `documents.file.download` | Yes | Yes | Signed 15-minute capability | Capability remains user/scope/observation/evidence/document bound |
| Auditor with inactive/missing `audit_readonly` | No | No | No | `403`/nondisclosing `404`, denial audited |
| Operational role holding copied observation permission codes | No | No | No | Role boundary rejects forgery; denial audited |
| Unauthenticated/invalid session | No | No | No | Existing `401` contract plus observation denial audit |
| Guessed/wrong-family/cross-observation source UUID | No | No disclosure | No | Nondisclosing `404`, denial audited |
| Revoked document permission or tampered/expired capability | Observation retained | Safe metadata remains | No | Nondisclosing `404`, denial audited |

Observation permissions never imply application, loan, document, workflow, configuration, audit-log,
or compliance-record mutation.

Verified by:

- `evidence/terminal-logs/audit-observation-permissions-green.log`
- `evidence/terminal-logs/audit-observation-evidence-green.log`
- `evidence/terminal-logs/focused-final-checks.log`
- `evidence/terminal-logs/reverse-consumer-suite-final.log`
