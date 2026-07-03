# Execution Plan

Selected slice: 002E2-frontend-role-bridge-hardening

## Scope
- Harden the frontend staff auth bridge so backend roles without prototype equivalents never fall back to auditor/admin/borrower UI behavior.
- Keep route and sidebar visibility permission-driven through the existing explicit backend-to-prototype permission mapping.
- Preserve borrower portal demo auth and staff demo auth behind `VITE_ENABLE_DEMO_AUTH === "true"`.

## Source Basis
- `docs/working/digests/epic-002-platform-auth.md` records the relevant source extracts: `/auth/me/` returns roles, teams, permissions, and available actions; role-aware UI navigation is required; backend role catalogue includes `it_head` and `management_viewer`.
- Architecture review `2026-07-03_224536_architecture_review` found the unsafe `auditor` fallback in `mapBackendUserToFrontendUser()`.

## Plan
1. Inspect the current auth-session mapping, role context, shell navigation, dashboard, and profile role branches.
2. Add failing frontend tests for zero-permission `it_head` and `management_viewer` sessions through the public auth/session and shell behavior where available.
3. Replace unsafe role fallback with a neutral staff role path that preserves backend role code/name display but grants no prototype permissions unless canonical backend permissions map explicitly.
4. Audit touched protected-shell role branches so neutral/zero-permission staff do not inherit auditor-specific dashboard/profile/action affordances.
5. Run focused frontend tests, then full frontend tests, typecheck, and build; run backend gates or document unchanged frontend-only scope if unavailable.
6. Save Ralph artifacts: terminal evidence, changed files, risk assessment, review packet, final summary, state/progress/handoff/slice status, and sharpen the next 1-2 Not Started slices using already-opened digest/source extracts.
