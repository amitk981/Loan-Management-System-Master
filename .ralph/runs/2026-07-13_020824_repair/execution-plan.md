# Execution Plan

Selected slice: 006Z8-portal-limit-provenance-module-and-interaction-closure

1. Use the prior trusted-browser command as the tight feedback loop and preserve its exact symptom:
   all four cases time out waiting for the routed portal's `New Application` button, so no declared
   screenshots are written.
2. Inspect the real portal session bootstrap and established portal E2E login/session pattern. Rank
   and test only hypotheses that explain why `/` never renders the authenticated portal dashboard.
3. Add a focused regression at the trusted browser seam, run it red where the sandbox permits, and
   change only the browser fixture/bootstrap demonstrated to be wrong. Do not change production
   behavior or weaken the four UI assertions.
4. Re-run Playwright collection and the focused browser spec locally. If Chromium is blocked by the
   documented macOS sandbox failure, preserve that evidence and rely on Ralph's two independent
   trusted runs for acceptance.
5. Run configured frontend/backend gates, save evidence and required run artifacts, audit protected
   paths/diff limits, and correct state/progress/handoff only after the repair is green.

Risk controls: no protected/source edits; preserve the uncommitted 006Z8 implementation; no fabricated
screenshots; no client-side financial or authority logic; no broad portal or production-code changes.
