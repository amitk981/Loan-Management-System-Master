# Risk Assessment

Risk level: High (standing approval; no revocation found).

- Protected PAN/Aadhaar use the existing token/hash boundary; only masks enter API/history and
  audit contains versions/field names only.
- Dedicated update permission, application object access, resource actions, and verifier/editor
  separation protect mutation without hard-coded roles.
- One additive migration adds optimistic version/update metadata and append-only history.
  Verification member/shareholding/folio/qualified fact/verifier/time cannot be patched.
- Row locking plus required version produces one-call 409 with no evidence write. PostgreSQL
  supplies production row locks; the local contract suite uses SQLite.
- Roll back code before the additive migration. Existing witness GET/POST remains compatible.
- Local browser collection passed; Ralph owns real Chromium/screenshots. None were fabricated.
