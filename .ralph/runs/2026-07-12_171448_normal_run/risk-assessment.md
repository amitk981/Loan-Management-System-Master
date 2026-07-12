# Risk Assessment

Risk level: High (owner standing approval)

- Scope is acceptance-only: one Playwright contract and Ralph evidence/state documents; no
  production code, schema, permissions, API behavior, source material, or visual styles changed.
- The flow performs real member writes under deterministic local E2E actors. Every created folio,
  PAN, Aadhaar, email, and signatory identity is unique per run; assertions require one create POST
  and one canonical detail GET, preventing retries or reuse of an earlier row.
- Protected values are supplied only to live local form inputs/request bodies. Screenshots and
  evidence describe or display masked values only; terminal output contains no generated values.
- Maker-checker risk is covered by a visible requester-denied state and a real Header sign-out before
  separate-checker approval. The approval action must be Registry-projected before the POST.
- Local Chromium cannot register its macOS Mach port in the coding sandbox. No screenshots were
  fabricated; the declared outside-sandbox two-run browser gate is the remaining acceptance control.
- Diff remains below Ralph limits and touches no protected path.
