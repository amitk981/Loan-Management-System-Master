# Browser Repair Diagnosis

## External trusted-browser failure

The authoritative first browser run reached real Django login, application listing, application
selection, and the selected application's detail GET. All three cases then failed in the common
helper with the same assertion:

```text
Locator: getByRole('heading', { name: 'Application Status', level: 2 })
Expected: visible
Received: <element(s) not found>
```

The rendered selected-detail component uses the level-two heading `Application LO000008L4`.
`Application Status` is the navigation label and is not a rendered heading. The repair changes only
that stale Playwright assertion.

## Local focused attempt

Command:

```text
RALPH_EVIDENCE_DIR=<repair-run>/evidence/screenshots \
E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python \
npm run e2e -- e2e/portal-disbursement-status.spec.ts --grep "current SAP-complete processing"
```

Result: the Django readiness server started, but sandboxed Chromium exited during launch with
`browserType.launch: Target page, context or browser has been closed`. Per the slice contract, this
is not treated as product failure and no screenshot was fabricated. Ralph's external validator
must execute the browser contract twice.
