# Risk Assessment

Risk level: High (inherited from the financial-authority slice)

- Selected slice: 006Z10-portal-limit-interaction-and-boundary-proof
- Mode: repair
- Repair blast radius: one test-only Playwright locator; no production behavior, data, permissions,
  money logic, schema, dependencies, or styling changed.
- Demonstrated risk: substring accessible-name matching selected both `Documents` and `My Documents`,
  preventing the trusted submit/refetch/reload scenario and its fourth screenshot from executing.
- Mitigation: require the existing wizard tab's exact accessible name and retain the full lifecycle
  assertions. All non-browser gates are green; two independent trusted browser runs remain the final
  acceptance authority.
- Standing approval: applies to the selected High-risk slice; no revoked action or protected path was
  touched.
