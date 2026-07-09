# Ralph Handoff

## Last Run
2026-07-09_190655_architecture_review

## Current Status
Architecture review completed successfully after `005C-reference-number-generation-and-loan-request-register`.

Reviewed product slices since prior architecture review commit `dadeefd`:
- `004K2-borrower-360-bank-holder-contract-hardening`
- `005A-loan-application-draft-create-update`
- `005B-application-submit-and-status-transition`
- `005C-reference-number-generation-and-loan-request-register`

Architecture review cadence is reset: `slices_completed_since_architecture_review = 0`.

## Review Findings
- Medium corrective issue: application detail and mutating actions (`GET/PATCH`, submit, and
  reference generation) currently enforce global permission codes but not loan-application object
  scope. Source `auth-permissions.md` requires application object access, including denial for a
  Field Officer viewing an unrelated application.
- Pass: `004K2` correctly closed the Borrower 360 bank-account holder-name DTO mismatch by using
  backend field `account_holder_name`.
- Pass: `005A`-`005C` have meaningful tests for envelopes, permissions, state transitions, audit,
  workflow events, sensitive-data exclusion, and `LO...` sequence/register behavior.

## Corrective Slice Created
`005C2-application-object-access-hardening` is now the next `Not Started` slice before `005D`.

It should:
- add failing-first regressions for unrelated same-permission users;
- reuse `sfpcl_credit.identity.modules.object_permissions.evaluate_object_access(...)`;
- enforce object access for application detail, draft update, submit, and reference-generation
  actions;
- preserve `403 PERMISSION_DENIED` for missing global permission and use
  `403 OBJECT_ACCESS_DENIED` for scope mismatch;
- prove denials create no update/submit/reference audit rows, workflow events, register rows, or
  visible sequence advancement;
- record any remaining Credit Manager/global credit-domain assumption if the current schema lacks
  queue/domain facts.

## Next Run
Run `005C2-application-object-access-hardening`.

After it passes, continue to `005D-application-document-checklist`; `005D` and `005E` have been
sharpened to reuse the corrected application object-access boundary.

## Evidence
See `.ralph/runs/2026-07-09_190655_architecture_review/`.

Key artifacts: `execution-plan.md`, `review-packet.md`, `risk-assessment.md`,
`changed-files.txt`, `final-summary.md`, and gate/review logs under `evidence/terminal-logs/`.
