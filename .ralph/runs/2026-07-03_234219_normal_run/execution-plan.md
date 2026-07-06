# Execution Plan

Selected slice: 002EX-early-end-to-end-tracer-bullet

## Scope
- Implement one thin full-stack tracer path only: member -> loan application -> sanction -> loan account -> disbursement -> repayment -> closure.
- Keep domain fields minimal per slice: ids/references/status/amount/member links/timestamps.
- Do not implement eligibility, interest, documentation, approval authority, exception paths, reports, or real servicing rules.

## Permissions Checked
- Allowed edit areas: `sfpcl_credit/**`, `sfpcl-lms/src/**`, `docs/working/**`, `docs/slices/**`, `.ralph/runs/**`, `.ralph/state.json`, `.ralph/progress.md`.
- Forbidden/protected areas will not be edited: `docs/source/**`, `scripts/**`, `.ralph/config.yaml`, `.ralph/permissions.json`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, high-risk/policy/design guardrails.

## Source Basis
- `docs/source/api-contracts.md` §3, §4-6: versioned `/api/v1/`, standard envelopes, explicit workflow action endpoints, backend-enforced transitions, auditability.
- `docs/source/data-model.md` §26.1-26.2: append-only audit logs and workflow events.
- `docs/working/digests/epic-002-platform-auth.md`: 002E/002E2 auth shell and neutral backend-role bridge behavior.

## Implementation Plan
1. RED: add backend integration tests for the full authenticated tracer path, out-of-order transition rejection, unauthenticated `401`, revoked access-token `401 INVALID_TOKEN`, and audit/workflow evidence.
2. GREEN: add a minimal `sfpcl_credit.tracer` app with models, service-layer transition guards, audited views, URL routes, and one migration.
3. RED/GREEN frontend: add tests for the narrow tracer permission bridge and zero-permission/neutral-role hiding.
4. Add a tracer API client and one staff-shell page using existing shell/sidebar/page patterns only; expose navigation/action only when the backend user has explicit tracer permission.
5. Update working docs: API contracts, MVP tracer bullet, assumptions, prototype inventory/gap report, digest extracts, handoff/progress/state/slice status.
6. Run backend and frontend quality gates with the orchestrator Python interpreter and save logs/evidence, including API samples and visual/smoke artifacts.

## Tracer Permission Decision
- Use one canonical permission code, `tracer.lifecycle.run`, to avoid granting existing broad finance/member permissions just for this dev tracer.
- Record this as a tracer-only assumption and keep zero-permission/unmapped roles with no tracer navigation/actions.
