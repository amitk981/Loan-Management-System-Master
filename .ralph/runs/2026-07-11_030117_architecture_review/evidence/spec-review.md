# Independent Spec Review

1. **High — 006H2 action authority remains synthesized.** Global permission codes are unioned with
   resource actions, the appraisal response supplies no resource action projection, and the real
   legacy remediation action is unavailable.
2. **High — mandated real-container interaction coverage is missing.** Static markup and direct API
   wrapper tests do not satisfy 006H2's click/HTTP/state/denial/stale matrix.
3. **Medium — malformed witness JSON escapes the required 400 envelope.** `parse_json_body` raises
   Django `ValidationError`, but the witness adapter catches only `WitnessValidationError`.
4. **Medium — witness folio evidence is not persisted.** GET reselects a current shareholding or
   mutable member folio rather than returning verification-time evidence.
5. **Medium — approvals does not own the workflow event promised by 006G2.** Credit creates the
   event and reload searches for a latest event; the handoff creates only the case.

No material scope creep was found. 006E4 and 006F4 match their central behavior/acceptance
contracts. Functional-ID conclusions are recorded in the review-window and REVIEW_FINDINGS.

