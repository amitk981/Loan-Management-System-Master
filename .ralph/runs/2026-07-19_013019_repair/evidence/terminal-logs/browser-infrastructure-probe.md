# Browser Infrastructure Probe

The isolated safe-error Playwright case was invoked with the required real-Django interpreter and
run-local screenshot directory:

```text
RALPH_EVIDENCE_DIR=<current-run>/evidence/screenshots \
E2E_DJANGO_PYTHON=<ralph-venv>/bin/python \
npm run e2e -- e2e/portal-disbursement-status.spec.ts --grep "safe unavailable state"
```

The Django readiness endpoint returned HTTP 200 and Playwright collected the test, but the coding
sandbox closed Chrome immediately after launch, before page creation:

```text
Error: browserType.launch: Target page, context or browser has been closed
<launched> /Applications/Google Chrome.app/Contents/MacOS/Google Chrome ... --headless --no-sandbox
```

No screenshot was fabricated. The slice's external browser gate must run the declared spec twice
and create all three non-empty screenshots before the orchestrator commits the candidate.
