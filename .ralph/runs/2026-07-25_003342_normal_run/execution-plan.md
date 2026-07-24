# Execution Plan

Selected slice: 011PC-closure-frontend-wiring

1. Inspect the existing Loan Closure Hub, Epic 011 staff API seam, adjacent wired staff screens,
   focused tests, E2E fixtures, and screenshot conventions. Confirm exact backend response shapes
   already delivered by 011G-011J.
2. Add focused frontend tests first for closure reads, named readiness blockers, action requests,
   canonical refetches, role/action handling, state rendering, and the final mock-removal ratchet.
   Save the expected failing (RED) output under `evidence/terminal-logs/`.
3. Extend only the shared Epic 011 staff API seam needed by S58-S61 and wire
   `LoanClosureHub.tsx` to backend-owned readiness, closure, NOC, security-return, and archive
   projections. Reuse existing visual and interaction patterns; add no business calculation,
   styling system, dependency, or product fixture.
4. Update the declared trusted-browser spec for the seeded blocked-readiness scenario and save
   `closure-readiness-blockers.png` from two passing contract runs when the local browser is
   available. Preserve honest infrastructure evidence if Chromium cannot launch.
5. Run focused frontend tests through GREEN, the Epic 011 reverse-consumer tests, typecheck, lint,
   and build. Record commands, outputs, and exit status in the current run evidence folder.
6. Inspect targeted diffs and mock-removal searches, then complete the role/action/blocker matrix,
   risk assessment, review packet, and final summary. Leave orchestrator-owned state, progress,
   slice status, changed-files list, and mechanical handoff untouched.

Permissions checked before product edits:

- Allowed: `sfpcl-lms/src/**`, current `.ralph/runs/2026-07-25_003342_normal_run/**`, and the
  declared E2E spec under the frontend project.
- Forbidden/protected and excluded: `docs/source/**`, `scripts/**`, `.ralph/config.yaml`,
  `.ralph/permissions.json`, `.codex/config.toml`, `AGENTS.md`, `CLAUDE.md`, `.gitignore`, and
  binding decision/design policy files.
- No backend commands are currently planned. If inspection reveals a necessary backend check, every
  such command will use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`.
