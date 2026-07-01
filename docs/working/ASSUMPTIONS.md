# Assumptions

| ID | Assumption | Why Made | Source Checked | Affected Slice | Risk | Needs Confirmation | Date Added | Resolved | Notes |
|---|---|---|---|---|---|---|---|---|---|
| A-001 | The existing React/Vite app is the prototype visual reference, not production-complete implementation. | The repo currently has only frontend code with mock data. | `docs/source/technical-architecture.md`, `docs/source/api-contracts.md`, `sfpcl-lms/package.json` | Future product slices | Medium | No | 2026-07-01 | Backend/database work should start from source docs. |
| A-002 | Current quality gate starts with `npm run build` because lint/typecheck/unit test scripts are not configured. | `package.json` has only `dev`, `build`, `preview`, and placeholder `test`. | `docs/source/test-plan.md`, `sfpcl-lms/package.json` | Slice 001 | Low | No | 2026-07-01 | Add test infrastructure as a future slice. |
