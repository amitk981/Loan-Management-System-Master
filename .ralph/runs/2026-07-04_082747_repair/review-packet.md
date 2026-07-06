# Review Packet — 002FL Frontend Lint Baseline

## Result
Success.

## Scope
Introduced the frontend ESLint baseline for `sfpcl-lms/src` and kept existing UI behavior intact.

## Changed
- Added `sfpcl-lms/eslint.config.js` using flat config, ESLint recommended rules, TypeScript recommended rules, React Hooks recommended rules, and the React Refresh component-export rule.
- Added `npm run lint` and pinned approved lint dev dependencies in `sfpcl-lms/package.json` / `package-lock.json`.
- Fixed lint issues that were safe and local: hook dependency arrays, one `no-case-declarations` branch, and `prefer-const` in `RegistersHub`.
- Updated `HANDOFF.md` with the protected `.ralph/config.yaml` lint-gate flip request.
- Sharpened next slices `002G` and `002H` using already-opened Epic 002/digest context.

## Traceability
- Slice requirement says ESLint must run on the whole `sfpcl-lms/src/` tree. Code now runs `eslint src`; verified by `evidence/terminal-logs/lint-final.log`.
- Slice requirement says not to touch protected `.ralph/config.yaml`. It was not edited; `HANDOFF.md` requests the owner/operator to enable `quality_gates.lint`.
- Slice requirement says Playwright specs stay outside vitest. `vite.config.ts` was unchanged and existing vitest stayed scoped to source tests.
- Frontend design rules say no visual redesign. Edits do not change CSS classes, colors, layout structures, labels, navigation/permission tables, or screen composition.

## Evidence
- Frontend lint: `evidence/terminal-logs/lint-final.log`
- Frontend typecheck: `evidence/terminal-logs/typecheck-final.log`
- Frontend tests: `evidence/terminal-logs/test-final.log`
- Frontend build: `evidence/terminal-logs/build-final.log`
- Backend check: `evidence/terminal-logs/backend-check.log`
- Backend tests: `evidence/terminal-logs/backend-test.log`
- Backend migrations: `evidence/terminal-logs/backend-migrations-check.log`
- Backend coverage: `evidence/terminal-logs/backend-coverage.log`
- Diff/protected checks: `evidence/terminal-logs/diff-check.log`, `evidence/terminal-logs/protected-paths-scan.log`

## Notes For Reviewer
Three rule downgrades are documented in `final-summary.md` and `risk-assessment.md`: `no-unused-vars`, `no-explicit-any`, and the Fast Refresh export rule for known shared shell exports. This avoids broad prototype cleanup or file moves beyond the lint-baseline slice.
