# Risk Assessment — 006Y8 Sign-out Repair

Risk: High, inherited from the protected-identity and maker-checker slice.

The repair changes one locator in the trusted Playwright journey. It opens the existing profile menu
through the visible seeded full name instead of searching for an email that is only rendered after
the menu opens. It does not change production code, permissions, maker-checker rules, protected-
value handling, persistence, dependencies, API contracts, or visual design.

Residual risk is limited to outside-sandbox browser execution. Collection finds the exact declared
scenario, but Chromium cannot launch inside this sandbox because macOS denies Mach-port
registration. Independent validation must execute the scenario twice and verify all three declared
screenshots. No protected or forbidden path was modified by this repair.
