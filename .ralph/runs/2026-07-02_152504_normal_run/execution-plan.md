# Execution Plan

Selected slice: 002A-backend-scaffold-and-health-endpoint

## Scope

- Add a minimal Django backend scaffold under `sfpcl_credit/` aligned with the source-doc modular-monolith direction.
- Implement unauthenticated operational health endpoints only:
  - `GET /api/v1/health/live/`
  - `GET /api/v1/health/ready/`
  - `GET /api/v1/health/deep/`
- Return the standard API envelope shape with `success`, `data`, and `meta`.
- Do not add dependencies or edit package files; Django 5.0.6 is already available in the execution environment.
- Do not add database models or migrations in this slice.

## Permissions Checked

- Forbidden: `docs/source/**`, `.env*`, `.git/**`, secrets/credentials. None will be edited.
- Approval-required: package files, config files, scripts. None will be edited.
- Planned edits are new backend scaffold files, Ralph run artifacts, `docs/working`, `.ralph/state.json`, `.ralph/progress.md`, and the selected slice file.

## TDD Plan

1. Write one health API test file first using Django's public test client.
2. Run the health test and confirm it fails before scaffold code exists.
3. Implement the minimal scaffold and health views.
4. Run the focused health test until green.
5. Run the required Ralph build gate: `npm run build` inside `sfpcl-lms/`.

## Evidence Plan

- Save focused backend test output under `.ralph/runs/2026-07-02_152504_normal_run/evidence/terminal-logs/`.
- Save health API response examples under `.ralph/runs/2026-07-02_152504_normal_run/evidence/api-responses/`.
- Save build output via Ralph validation artifacts.
- Save `changed-files.txt`, `risk-assessment.md`, `review-packet.md`, and `final-summary.md`.
