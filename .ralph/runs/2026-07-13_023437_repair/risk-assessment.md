# Risk Assessment

Risk level: High (inherited from slice 006Z8).

This repair changes no production behavior. It changes the trusted-browser fixture and adds a
regression that requires the fixture to include every dashboard field used during render and to
enter MP05 through the rendered dashboard action.

The demonstrated risk was deterministic portal-tree loss: a nominally successful but incomplete
dashboard response caused `MP03DashboardView` to format undefined member fields, so React detached
or removed the navigation control. The fixture is now checked against `PortalDashboard` at compile
time and by a focused Vitest regression.

Remaining risk: Chromium cannot execute inside the coding sandbox because macOS denies its Mach-port
registration. Playwright collection passes, and Ralph's independent two-run browser validation must
confirm all four screenshots. No protected paths, dependencies, migrations, permissions, financial
rules, backend code, or production frontend code were changed by this repair.
