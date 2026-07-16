# Trusted Browser Local Evidence

Collection command:

```text
E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python \
RALPH_EVIDENCE_DIR=/tmp/ralph-008m3-browser-evidence \
npx playwright test e2e/staff-documentation-workspace.e2e.spec.ts --list
```

Result: one test collected successfully.

The real local run started the declared Django setup but Chromium exited before page creation:

```text
FATAL mach_port_rendezvous ... bootstrap_check_in ... Permission denied (1100)
```

This is the sandbox limitation described by the run prompt. No screenshot was fabricated and no
local browser failure is reported as product failure. The orchestrator must run this contract twice
outside the sandbox and produce:

- `documentation-checklist-blockers.png`
- `documentation-security-workflow.png`
- `documentation-restricted-state.png`
- `documentation-final-approval.png`
