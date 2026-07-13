# HTTP and immutable-evidence examples

- Collection GET projects `read/create`; each authorised row projects `read/update` and `version`.
- PATCH requires current version and name/PAN/Aadhaar only.
- Success test asserts version 2, PAN `******876P`, Aadhaar `********9876`; plaintext/token/hash is
  absent from response, history, and audit.
- Immutable member PATCH returns 400; stale version returns 409. Both preserve witness/history/audit.
- Shareholding UUID, folio, verifier, and verification time remain unchanged after correction.
