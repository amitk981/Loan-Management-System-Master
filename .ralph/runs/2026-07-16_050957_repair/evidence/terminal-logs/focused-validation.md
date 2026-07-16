# Focused validation

- `npm run build` — PASS (1,880 modules transformed).
- `npm run typecheck` — PASS.
- `npm run lint` — PASS.
- `npm test -- --run` — PASS (36 files, 319 tests).
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py check` — PASS.
- `/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py makemigrations --check --dry-run` —
  PASS (`No changes detected`).
- `npx playwright test e2e/staff-documentation-workspace.e2e.spec.ts --project=chromium --list`
  — PASS (one declared test collected).
- Real Playwright invocation — both servers started and Django health returned 200; Chromium then
  stopped before page creation with macOS `MachPortRendezvousServer ... Permission denied (1100)`.
  This is the documented sandbox limitation, not trusted-browser acceptance.
- `git diff --check` — PASS.
