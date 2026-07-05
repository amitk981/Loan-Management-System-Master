# Ralph Handoff

## Last Run
2026-07-05_193926_normal_run

## Current Status
Slice `003F-communication-template-shell` completed successfully.

## What Completed
- Added `sfpcl_credit.communications` with:
  - `ContentTemplate` mapped to `content_templates`.
  - One non-destructive migration: `communications/migrations/0001_initial.py`.
- Added protected content-template metadata APIs:
  - `GET /api/v1/content-templates/`
  - `POST /api/v1/content-templates/`
  - `PATCH /api/v1/content-templates/{content_template_id}/`
- Response items expose only metadata fields:
  `content_template_id`, `template_code`, `template_name`, `template_type`, `language_code`,
  `audience`, `subject_template`, `body_template`, `variables`, `approval_status`,
  `template_version`, `effective_from`, and `effective_to`.
- Validation covers required create fields, ISO dates, `effective_to >= effective_from`,
  `variables` as a JSON array of non-empty strings, `approval_status` limited to `draft`/`approved`,
  duplicate `template_code`, and unknown ids.
- Permission gates:
  - list/read: `communications.content_template.read` OR `communications.content_template.manage`
  - create/update: `communications.content_template.manage`
- A-022 records the source-catalogue gap and narrow permission handling. The catalogue seeds
  `communications.content_template.read/manage` and grants them to `compliance_team_member` as the
  current source-backed Compliance owner.
- Mutating actions write `AuditLog` rows:
  - `communications.content_template.created`
  - `communications.content_template.updated`
- Audit/response payloads deliberately exclude rendered borrower/loan-specific merge output.
- M16-FR-004 and M18-FR-006 are traced. M16-FR-001 through M16-FR-003 and M16-FR-005 through
  M16-FR-007 remain deferred: no email/SMS/letter sending, delivery status, manual phone-call
  logging, borrower/loan communication attachment, delivery queues, adapters, or notification UI.

## Working Docs Updated
- `docs/working/API_CONTRACTS.md`: content-template contract, validation, permissions, audit
  behavior, and deferrals.
- `docs/working/ASSUMPTIONS.md`: A-022 for content-template permission handling.
- `docs/working/digests/epic-003-audit-documents-config.md`: 003F implementation note and new
  dashboard/task extracts for 003G/003H.
- `docs/slices/003F-communication-template-shell.md`: marked Complete.
- `docs/slices/003G-dashboard-task-summary-api.md`: sharpened with concrete dashboard API fields,
  role contexts, permission guidance, and tests.
- `docs/slices/003H-dashboard-task-ui-wiring.md`: sharpened with concrete frontend API wiring,
  states, screenshot requirements, and tests.

## Evidence
See `.ralph/runs/2026-07-05_193926_normal_run/`:
- `evidence/terminal-logs/red-content-template-api-tests.log`
- `evidence/terminal-logs/green-content-template-api-tests.log`
- `evidence/terminal-logs/green-content-template-and-catalogue-tests.log`
- `evidence/terminal-logs/backend-check.log`
- `evidence/terminal-logs/backend-tests.log`
- `evidence/terminal-logs/backend-makemigrations-check.log`
- `evidence/terminal-logs/backend-coverage.log`
- `evidence/terminal-logs/frontend-typecheck.log`
- `evidence/terminal-logs/frontend-lint.log`
- `evidence/terminal-logs/frontend-tests.log`
- `evidence/terminal-logs/frontend-build.log`
- `evidence/api-responses/content-template-api-response.txt`

## Current Blocker
None.

## Next Recommended Action
Run `003G-dashboard-task-summary-api`.

Notes for `003G`:
- Use the new "Dashboard and Task Foundation Extracts" section in the Epic 003 digest before opening
  large source docs.
- Build only `GET /api/v1/dashboard/` as a role-based summary shell.
- Return source-named zero-count cards and empty tasks where underlying modules/tables do not exist;
  do not invent loan/compliance/treasury calculations.
- Resolve the dashboard permission gap explicitly in `ASSUMPTIONS.md`; do not silently reuse broad
  report/export permissions unless the source extract supports the read scope.
