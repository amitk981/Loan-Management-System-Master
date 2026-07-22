# Trusted Browser RED

Authoritative source:
`.ralph/runs/2026-07-22_173435_normal_run/evidence/terminal-logs/trusted-browser-acceptance-1.log`

Command:
`RALPH_EVIDENCE_DIR=<run-1> E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/recovery-action-execution.e2e.spec.ts`

Observed trusted behavior:

- Chrome launched and the real login path succeeded.
- `S57 blocks execution when no approved action is exposed` failed waiting for
  `Security Invocation Locked`; its fixture used invalid `total_pages: 0` and the client rendered a
  malformed-response state.
- `S57 renders the exact approved route and evidence controls` timed out waiting for
  `Default & Recovery`; the mocked Company Secretary's two canonical recovery permissions were not
  mapped to the frontend's existing `manage_defaults` navigation gate.
- Result: 2 failed; exit code 1; screenshot evidence exit code 1.
