# Ralph Handoff

## Last Run
2026-07-11_133237_normal_run

## Current Status

006H4 is complete. Eligibility, loan-limit, appraisal, appraisal-transition, and sanction HTTP
success responses carry the standard resource-level action projection. The real workbench no
longer unions `/auth/me.available_actions`; current-user permission/role checks only narrow enabled
resource actions. Legacy prerequisite remediation is advertised distinctly. Writable PATCH
projection and the exact 006G3 sanction workflow-event identity remain unchanged.

## Validation

Evidence is under `.ralph/runs/2026-07-11_133237_normal_run/`. Frontend build, typecheck, lint, and
138 tests passed. Django check/migration sync and 394 backend tests with five expected skips passed
at 94% coverage.

## Next Run

Architecture review remains due. Then run 006H3 to restore prototype fidelity without weakening
006H4 action authority, followed by the sharpened 006X cross-role tracer.
