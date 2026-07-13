# Trusted Browser Navigation — Red Evidence

Feedback command used by independent validation:

`RALPH_EVIDENCE_DIR=... E2E_DJANGO_PYTHON=/Users/amitkallapa/LMS/.ralph/venv/bin/python npm run e2e -- e2e/portal-application-limit-authority.e2e.spec.ts`

The two saved trusted runs in `2026-07-13_020824_repair` both collected four tests and failed all
four before MP05 mounted. The minimal repeated symptom was:

```text
locator resolved to <button ...>New Application</button>
attempting click action
waiting for element to be visible, enabled and stable
element was detached from the DOM, retrying
Test timeout of 30000ms exceeded.
```

This is red-capable for the exact external failure: the real member-login path succeeds far enough
to resolve the portal navigation control, but Playwright's pointer actionability phase races the
portal shell remount and never enters the routed `New Loan Application` screen.
