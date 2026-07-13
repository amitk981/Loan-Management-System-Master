# Risk Assessment

Risk level: High (inherited slice classification); repair delta is test-only.

- Selected slice: 006Y3-member-registry-and-identity-change-approval-closure
- Mode: repair
- Demonstrated risk: both trusted browser runs reached the intended denied mutation, but the E2E
  spec expected the retired `PERMISSION_DENIED` code and stopped before the fifth screenshot.
- Repair: only the declared E2E spec changed, replacing the stale code with the canonical
  authenticated permission-denial code `FORBIDDEN`. Production permissions, storage, audit,
  member identity, and approval behavior are unchanged.
- Residual risk: local sandboxing prevents Chromium from executing the repaired body. Playwright
  collection and all non-browser gates pass, but two independent trusted runs must confirm the
  complete workflow and all five screenshots before commit.
- Privacy/security: fixtures remain synthetic and the denial still exercises a real session and
  real protected endpoint; no identity plaintext was added to durable output.
- Protected paths: no protected or forbidden file was modified by this repair.
