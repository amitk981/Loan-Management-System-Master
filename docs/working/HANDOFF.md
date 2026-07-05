# Ralph Handoff

## Last Run
2026-07-05_191550_normal_run

## Current Status
Slice `003E-versioned-configuration-shell` completed successfully.

## What Completed
- Added `sfpcl_credit.configurations` with:
  - `LoanPolicyConfig` mapped to `loan_policy_configs`.
  - `VersionHistory` mapped to `version_histories`.
  - One non-destructive migration: `configurations/migrations/0001_initial.py`.
- Added protected loan-policy configuration APIs:
  - `GET /api/v1/config/loan-policy/`
  - `POST /api/v1/config/loan-policy/`
  - `PATCH /api/v1/config/loan-policy/{loan_policy_config_id}/`
  - `POST /api/v1/config/loan-policy/{loan_policy_config_id}/activate/`
- Added protected version-history API:
  - `GET /api/v1/version-histories/?versioned_entity_type=loan_policy_config&versioned_entity_id=uuid`
- Permission gates:
  - loan-policy list/read: `config.loan_policy.read`
  - loan-policy create/update/activate: `config.loan_policy.manage`
  - version history read: `audit.version_history.read`
- Mutating config actions write `AuditLog` rows:
  - `config.loan_policy.created`
  - `config.loan_policy.updated`
  - `config.loan_policy.activated`
- Activation writes a `VersionHistory` row and blocks activation unless
  `board_approval_reference` is present, covering M01-FR-015 for this shell.
- A-021 records the source-silent retirement behavior: activating a new draft config retires any
  previously active config and sets its `effective_to` to the day before the new effective date.
- M01-FR-003 through M01-FR-014 remain explicitly deferred; 003E did not implement eligibility,
  share valuation, scale-of-finance, approval matrix, interest, charges, document-template,
  re-KYC, compliance-frequency calculations, or broader config types.

## Working Docs Updated
- `docs/working/API_CONTRACTS.md`: versioned loan-policy and version-history contracts, validation,
  permissions, audit behavior, and requirement trace.
- `docs/working/ASSUMPTIONS.md`: A-021 for activation retirement semantics.
- `docs/working/digests/epic-003-audit-documents-config.md`: 003E implementation note and deferrals.
- `docs/slices/003E-versioned-configuration-shell.md`: marked Complete.
- `docs/slices/003F-communication-template-shell.md`: sharpened with response fields and
  permission-boundary guidance.

## Evidence
See `.ralph/runs/2026-07-05_191550_normal_run/`:
- `evidence/terminal-logs/red-loan-policy-list-test.log`
- `evidence/terminal-logs/green-loan-policy-list-test.log`
- `evidence/terminal-logs/red-configuration-api-tests.log`
- `evidence/terminal-logs/green-configuration-api-tests.log`
- `evidence/terminal-logs/backend-check.log`
- `evidence/terminal-logs/backend-tests.log`
- `evidence/terminal-logs/backend-makemigrations-check.log`
- `evidence/terminal-logs/backend-coverage.log`
- `evidence/terminal-logs/frontend-typecheck.log`
- `evidence/terminal-logs/frontend-lint.log`
- `evidence/terminal-logs/frontend-tests.log`
- `evidence/terminal-logs/frontend-build.log`
- `evidence/terminal-logs/git-diff-check.log`
- `evidence/api-responses/loan-policy-api-response.txt`

## Current Blocker
None.

## Next Recommended Action
Run `003F-communication-template-shell`.

Notes for `003F`:
- Use the existing digest section before opening large source docs.
- Build only the content-template metadata/API shell.
- Do not implement send/list communications, delivery retries, SMTP/SMS adapters, notification UI,
  or borrower/loan communication records.
- Resolve the content-template permission gap explicitly in `ASSUMPTIONS.md`; do not silently grant
  broad communication/template access or reuse unrelated `config.loan_policy.*` permissions.
