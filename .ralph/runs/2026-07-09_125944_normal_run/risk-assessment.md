# Risk Assessment

Selected slice: `004G-landholding-and-crop-plan-records`

Risk level: Medium

## Why
- Adds two member-master evidence tables and one database migration.
- Adds authenticated API endpoints and permission checks.
- Adds Member Profile create/list UI paths.
- Does not implement financial calculations, eligibility blockers, verification workflows, or
  sensitive-data reveal.

## Controls Applied
- TDD evidence saved for backend and frontend red/green cycles.
- Backend permissions tested for missing auth, read/create separation, and denied access.
- Create audit metadata tested for land holdings and crop plans; workflow event count remains zero.
- Validation tested for positive acreage, required land document ID, and malformed UUID fields.
- API contract and assumption docs updated.
- Full quality gates passed.

## Residual Risks
- A-032 is a permission assumption: source docs do not define land/crop-specific permission codes,
  so 004G uses `members.member.read` for list and `members.member.update` for create.
- Land/crop verification actions and detail/update endpoints are deferred.
- Loan-limit and eligibility behavior is intentionally absent; later slices must not infer those
  rules from the presence of land/crop records alone.

## Protected Path Review
No protected files were modified. `docs/source/`, `scripts/`, `.ralph/config.yaml`,
`.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`,
`docs/working/HIGH_RISK_APPROVALS.md`, and `docs/working/DECISION_POLICY.md` were not edited.
