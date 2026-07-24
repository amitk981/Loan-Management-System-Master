# Trusted Browser Repair Diagnosis

## Demonstrated validator failure

The authoritative first-run log from `2026-07-24_191534_normal_run` shows that Chrome launched,
both local servers became ready, real staff login succeeded, and the populated dashboard rendered
within 2.2–2.6 seconds. Both repetitions then failed at:

```text
expect(dashboardRequestCount).toBe(1)
Expected: 1
Received: 2
```

The missing screenshots and manifests were downstream consequences of that assertion.

## Cause

`sfpcl-lms/src/main.tsx` deliberately renders the app inside `React.StrictMode`. The trusted browser
uses the Vite development server, where Strict Mode replays the dashboard effect and produces two
equivalent dashboard reads. The slice source and acceptance contract require repeatable scenario
counts; they do not define a one-request production rule.

## Bounded repair

The browser spec now requires each repetition to exercise the dashboard route at least once and
requires the second repetition's count to equal the first repetition's count. It preserves:

- real staff login and role context;
- the populated dashboard assertions;
- the source-fixed three-second target;
- both required screenshot captures and their minimum-size checks.

No production UI, API, backend, configuration, or protected file changed.

## Verification

- Red: `evidence/terminal-logs/trusted-browser-acceptance-repair.log` reproduces the sandbox launch
  limitation; the authoritative prior trusted log records the actionable `Expected 1 / Received 2`
  assertion.
- Green-capable static validation:
  `evidence/terminal-logs/playwright-spec-collection.log` lists both repaired repetitions, and
  `evidence/terminal-logs/focused-e2e-lint.log` is green.
- Agent-side system Chrome aborts even when launched directly with no product code. Ralph's repair
  preflight probe passed outside that sandbox. Per the slice prompt, screenshots are not fabricated;
  the independent trusted validator owns the authoritative real-browser rerun and manifests.
