# Risk Assessment

Risk level: High.

The underlying slice governs protected member identity and checker authority. This repair does not
change production member behavior, identity storage, role defaults, API contracts, or migrations.
It changes only the trusted browser contract and the isolated E2E actor fixture needed to exercise
the already-implemented requester/checker path.

Controls:

- The E2E manager grant is confined to `seed_e2e_users`, which refuses to run without explicit
  debug and E2E guards and uses an isolated database.
- A failing-first backend test proves the synthetic checker has exactly the required member read
  and approval capabilities.
- The browser contract uses real login/API paths, distinct actors, canonical GETs after every
  success, and a direct `403 PERMISSION_DENIED` assertion for the zero-permission actor.
- No source, protected file, dependency, production role assignment, or production styling changed.
- Local browser execution was blocked before the test body by macOS Mach service sandboxing; final
  browser risk remains with Ralph's mandatory two-run independent acceptance gate.
