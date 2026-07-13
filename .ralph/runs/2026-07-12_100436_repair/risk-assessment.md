# Risk Assessment

Risk level: High.

The slice governs protected member identity and approval authority. This repair is narrowly scoped
to the demonstrated member-update failure: it converts the existing membership date to an ISO
string before old/new values enter JSON change history. It does not change permissions, protected
identity storage, approval rules, API payloads, migrations, frontend behavior, or styling.

Controls:

- A failing-first API test reproduced the exact `TypeError: Object of type date is not JSON
  serializable` through the public member PATCH path.
- The test now proves a `200` response and JSON-safe old/new date history.
- Full frontend/backend gates pass, including 415 backend tests and 94% coverage.
- No protected/source file, dependency, or schema changed in this repair.
- Local Chromium is sandbox-denied before the test body; Ralph's mandatory unsandboxed two-run
  browser acceptance remains responsible for the five declared screenshots.
