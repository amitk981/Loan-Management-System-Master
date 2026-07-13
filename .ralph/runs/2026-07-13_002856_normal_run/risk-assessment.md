# Risk Assessment

Risk level: Medium

- Selected slice: 006Z2-portal-application-limit-display-authority
- Mode: normal_run
- Financial display authority moved to a server-owned calculation shared with staff credit logic.
- Portal scope derives only from the authenticated active PortalAccount; the endpoint accepts no
  member identifier and returns no member, evidence, verifier, decision, configuration, or action IDs.
- Stale, future, closed, manual, mismatched, incomplete, or contradictory authority/facts fail to an
  explicit unavailable projection rather than zero or a guessed amount.
- No schema, dependency, protected-file, source-file, external-system, or destructive change.
- Residual risk: policy/evidence updates between reads can change a displayed projection; the endpoint
  intentionally recomputes canonical current facts and submission remains governed by backend rules.
- Chromium visual capture was blocked by sandbox services, not by application behavior; mounted and
  static visual evidence is retained for review.
