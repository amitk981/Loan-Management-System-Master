# Risk Assessment — 006Y8 Browser Repair

Risk: High, inherited from the protected-identity and maker-checker slice.

The repair changes only the trusted Playwright journey. After each required full page reload, it
re-enters the same application through the real staff Applications UI before asserting canonical
persisted values. It does not change production code, API contracts, permissions, maker-checker
rules, protected-value handling, storage, dependencies, styling, or quality gates.

Residual risk is limited to outside-sandbox browser behavior. The scenario collects exactly once,
but Chromium cannot launch in the coding sandbox because macOS Mach-port registration is denied.
The orchestrator must execute the scenario twice and verify all three declared screenshots. No
protected or forbidden path was modified.
