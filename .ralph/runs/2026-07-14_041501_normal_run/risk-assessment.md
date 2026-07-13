# Risk Assessment

Risk level: High (owner standing approval; no veto)

This slice changes the source of formal sanction decisions and the Credit Sanction Register, so a
defect could misstate financial/compliance evidence. It also adds one additive database field:
`credit_sanction_register_entries.source_review_facts_json`, defaulting to an empty object for
existing immutable rows.

Controls applied:

- Final approval/rejection holds the existing application -> appraisal -> case locks and re-runs
  canonical frozen-package validity before any action and immediately before decision/register
  creation.
- New decisions and register fields copy the routed package only; mutable owner records remain
  transition/foreign-key owners but are not terminal value sources.
- Malformed frozen truth rolls back action, decision, register, audit, workflow, communication, and
  notification writes.
- Existing optimistic version, historical-cycle, communication atomicity, and race logic is
  unchanged and covered by the full suite.
- General Meeting scope remains permission-, legal-audience-, object-, and document-authority
  checked while using the shared readable-case decision.

Residual risk: existing register rows have `{}` in the new source-package field because historical
rows cannot be truthfully reconstructed. They remain readable through their existing immutable
scalar fields; 007Q must treat missing historical source-only display facts as null rather than
consulting live owners. No deployment, paid service, real communication, or protected-file change
was performed.
