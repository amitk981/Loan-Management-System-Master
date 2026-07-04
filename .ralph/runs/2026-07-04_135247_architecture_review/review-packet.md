# Review Packet: 2026-07-04_135247_architecture_review

## Result
Complete — independent architecture review, no production code changed.

## Slice
architecture-review

## Diff Window
Reviewed slice commits merged since the prior architecture review commit `0939e01`:
- `e8a166f` — `002EYA-e2e-baseline-and-seed-safety`
- `17a85e6` — `002F2-navigation-render-regression-tests`
- `dd223ea` — `002G-admin-user-and-role-management-shell`
- `fd020d9` — `002H-state-machine-and-transition-guard-foundation`

Also considered operator baseline commit `9c4e97b` because it completed the screenshot-baseline evidence required by 002EYA. Non-slice workflow/operator commits in the same git window were not production-code review targets.

## Findings
1. **Medium — 002G collapses distinct user-admin permissions into one backend authority.** `admin_users.has_manage_users_permission()` grants full list/detail/role/team/status power when the actor has any one of `users.user.create`, `users.user.update`, or `users.user.disable`. Source `auth-permissions.md` §12.1 defines those separately and marks disable Critical. Corrective slice created: `002G2-admin-user-action-permission-granularity`.
2. **Low — Admin Users screen lacks screenshot evidence.** The implementation reuses existing visual patterns, but 002G could not capture browser screenshots because the in-app browser target was unavailable. If 002G2 touches frontend action visibility, it must save visual evidence.
3. **Pass — 002EYA/002F2 closed prior review gaps.** Screenshot baselines now exist, E2E seed safety has runtime guards/tests, and the run evidence directories referenced by packets now exist.
4. **Pass — 002H introduced a useful domain-neutral workflow guard.** The guard accepts explicit transition definitions and actor permissions, and tracer regression tests preserve existing endpoint behavior.

Full wording is appended newest-first in `docs/working/REVIEW_FINDINGS.md`.

## Standards Axis
- No production-code edits were made in this review run.
- Reviewed frontend changes stay within the existing visual system; no color/typography/layout redesign was found.
- Significant architecture drift found in 002G's permission boundary: backend authorization collapses distinct canonical permissions into a coarse management gate.
- Test-quality gap found for 002G: no tests with partial user-admin permission roles.
- Prior evidence-path issue is materially improved: current reviewed run packets reference nested `evidence/terminal-logs/` files that exist.

## Spec Axis
- 002EYA satisfies the seed-safety and baseline-capture intent when combined with the operator baseline commit; the agent sandbox still cannot run full browser E2E because local web-server startup is denied.
- 002F2 satisfies the corrective navigation-render requirement using a pure helper consumed by `Sidebar`.
- 002G satisfies the main admin user shell flow but is partial against the source RBAC model because separate create/update/disable permissions are not enforced separately.
- 002H satisfies the shared state-machine guard foundation and keeps the guard domain-neutral.
- Functional-spec requirement-ID sweep: no `M##-FR-###` IDs were present in the reviewed Epic 002 digest/slice files; Epic 002 remains in progress.

## Corrective Slices Created / Sharpened
- Created `docs/slices/002G2-admin-user-action-permission-granularity.md`.
- Sharpened `docs/slices/002I-object-level-permission-test-harness.md` to depend on 002G2 and avoid coarse permission names.
- Sharpened `docs/slices/002J-api-contract-test-harness.md` to include 002G2 partial-permission `403` fixture coverage.
- Updated `docs/working/digests/epic-002-platform-auth.md` with the source extracts used for 002G2.

## Gates Run In This Review
- Frontend: `npm run lint`; `npm test -- --run` (26/26); `npm run typecheck`; `npm run build`.
- Backend: `manage.py check`; backend tests (75/75); `makemigrations --check --dry-run`; coverage 95% with fail-under 85.
- Diff hygiene: `git diff --check`.

Evidence is saved under `.ralph/runs/2026-07-04_135247_architecture_review/evidence/terminal-logs/`.

## Recommended Next Action
Run `002G2-admin-user-action-permission-granularity`, then `002I-object-level-permission-test-harness`.
