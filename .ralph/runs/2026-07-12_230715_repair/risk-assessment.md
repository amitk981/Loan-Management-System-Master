# Risk Assessment

Risk level: High (inherited from member identity governance).

- Selected slice: `006Y13-member-mutation-success-interaction-closure`
- Mode: repair
- The repair changes one production serialization boundary: protected-identity requests now contain
  only optimistic `version`, changed PAN/Aadhaar fields, and the reason.
- It does not change backend behavior, permissions, maker-checker rules, schemas, dependencies,
  styling, or protected files. The preceding unchanged-masked-mobile PATCH repair is preserved.
- Primary risk: dropping a protected field intended for correction. Mitigation: both PAN and Aadhaar
  are included when entered, and the exact shared-HTTP test asserts the complete request body.
- Local Chromium is sandbox-blocked. Independent validation must execute the declared spec twice and
  verify all five screenshots before any commit.
