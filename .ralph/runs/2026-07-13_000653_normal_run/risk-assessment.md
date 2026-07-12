# Risk Assessment

Risk level: High (owner standing approval; no revoke entry found).

- Security impact: improves object non-disclosure by eliminating a parent-application existence
  oracle on witness PATCH. Permission checks still precede parent resolution.
- Behavioral impact: missing update permission retains `403 FORBIDDEN` but its message now exactly
  matches the projected action reason. Unknown parent IDs on authorized PATCH callers now return
  `403 OBJECT_ACCESS_DENIED` rather than `404`, deliberately preventing enumeration.
- Data integrity: all denial classes assert byte-equivalent witness rows and unchanged correction
  history, audit, and workflow evidence. Success remains versioned, transactional, and audited.
- Blast radius: three backend product/test files; no schema, frontend, dependency, external service,
  source, or protected-path change.
- Residual risk: trusted browser screenshots are external-gate artifacts; local collection confirms
  the exact declared contract but does not fabricate browser output.
- Rollback: revert the application resolver/view use and matrix tests together. Doing so reopens the
  documented enumeration path and is not recommended.
