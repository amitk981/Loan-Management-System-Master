# Review Packet: 2026-07-04_085117_architecture_review

## Result
Complete — independent architecture review, no production code changed.

## Slice
architecture-review

## Diff Window
Reviewed commits merged since the prior architecture review commit `ba78859`:
- `0cb56c3` — `002EY-e2e-and-visual-regression-harness`
- `84ba391` — `002F-role-aware-sidebar-header-navigation`
- `cc0c134` — `002FL-frontend-lint-baseline`

Review commands:
- `git diff --stat ba78859...HEAD`
- `git diff --name-only ba78859...HEAD`

## Findings
1. **Medium — 002EY authored Playwright tests but did not complete the visual-regression contract.** The E2E specs call `toHaveScreenshot()`, but no `sfpcl-lms/e2e/*-snapshots/` PNG baselines are committed. The 002EY packet also says first baseline generation remains an operator step, so `npm run e2e` is not yet a normal green gate from a clean checkout. Corrective slice: `002EYA-e2e-baseline-and-seed-safety`.
2. **Medium — `seed_e2e_users` creates known-password active users without an explicit E2E guard.** It is intended for the isolated Playwright sqlite DB, but the management command itself would seed `E2eTracer123!` users into whatever DB it is pointed at. Corrective slice: `002EYA`.
3. **Medium — 002F's Sidebar hiding test is too shallow.** The implementation filters nav items by permission, but the test named "hides every protected sidebar item" only checks a constructed permission set; it would pass even if `Sidebar` stopped filtering. Corrective slice: `002F2-navigation-render-regression-tests`.
4. **Medium — reviewed run packets again reference missing `evidence/terminal-logs/` paths.** Root gate logs exist, but the nested evidence dirs named in the packets/progress entries for 002EY, 002F, and 002FL are absent from committed artifacts. Corrective slices require real paths; owner/operator should inspect artifact preservation.
5. **Low — 002FL's packet overstates lint evidence.** The root lint gate was skipped because protected config still disables lint, and `final-summary.md` does not contain the rule-downgrade justifications the packet claims. Current review-run `npm run lint` passed; the issue is audit packet accuracy.
6. **Pass — 002F and 002FL's core implementation shapes are reasonable.** Shared route permissions, tracer permission isolation, neutral backend-staff handling, and lint-safe syntax changes are directionally sound. Current gates passed.

Full wording is appended newest-first in `docs/working/REVIEW_FINDINGS.md`.

## Standards Axis
- The reviewed production/frontend code stays within the existing visual system. No color, typography, layout, or component-style drift was found.
- ESLint dependencies are exact pinned and the config uses standard recommended packages, with documented rule downgrades in risk assessment.
- Architecture drift found: E2E seed command lacks a runtime safety guard despite predictable credentials.
- Test-quality gap found: navigation visibility tests do not exercise the actual Sidebar hiding behavior.

## Spec Axis
- 002EY partially satisfies the harness spec but misses committed screenshot baselines and normal-mode E2E proof.
- 002F satisfies the central route-guard extraction intent, but falls short of the slice requirement to prove every nav item is hidden for users lacking its permission.
- 002FL satisfies the code/config portion of the lint baseline, but historical run evidence did not actually preserve the claimed lint log path.
- Functional-spec requirement-ID sweep (`M##-FR-###`): no such IDs were present in the reviewed Epic 002 files/digest, and Epic 002 is still in progress, so no full-epic ID reconciliation is owed this review.

## Corrective Slices Created / Sharpened
- Created `docs/slices/002EYA-e2e-baseline-and-seed-safety.md`.
- Created `docs/slices/002F2-navigation-render-regression-tests.md`.
- Sharpened `docs/slices/002G-admin-user-and-role-management-shell.md` to depend on both corrective slices and extend the shared navigation contract.
- Updated `docs/working/digests/epic-002-platform-auth.md` with the review extracts for the next agents.

## Gates Run In This Review
- Frontend: `npm run lint`, `npm test` (23/23), `npm run typecheck`, `npm run build`.
- Backend: `manage.py check`, backend tests (64/64), `makemigrations --check --dry-run`, coverage 95% with fail-under 85.
- Diff hygiene: `git diff --check`.

Evidence is saved under `.ralph/runs/2026-07-04_085117_architecture_review/evidence/terminal-logs/`.

## Recommended Next Action
Run `002EYA-e2e-baseline-and-seed-safety`, then `002F2-navigation-render-regression-tests`, before `002G-admin-user-and-role-management-shell`.
