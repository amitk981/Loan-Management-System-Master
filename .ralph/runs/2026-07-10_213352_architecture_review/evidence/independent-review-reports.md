# Independent Review Reports

Fixed point: `46442fe7892d3ad7aa9f4251a9f5f01442ff4a9a`

Diff: `git diff 46442fe...HEAD`

Commits: `cd3aca6` 006E3, `b022c83` 006F3, `b1b8889` 006G, `b7cf63f` 006H.

## Standards

- Critical/hard: 006F3 and 006G completed without executing their mandatory PostgreSQL concurrency
  suites. This violates their slice acceptance and Decision Policy §2.
- High/hard: the workbench recreates action availability from local role/permission/status facts
  and hard-codes submitted states that the response does not contain. This violates codebase-design
  §23.3-§23.4 and 006H's no-synthesis rule.
- High/hard: 006H replaces the approved staged workbench and rewrites checklist/calculator layouts,
  violating the binding Frontend Design Rules; there is no visual proof.
- High/test quality: static-markup tests never run container effects or click an action, contrary to
  codebase-design §26.3 and the slice's action-test requirement.
- Medium/hard: malformed/non-object sanction JSON can escape the standard validation envelope.
- Medium/hard: a new bespoke fetch implementation duplicates and weakens shared transport behavior.
- Medium/judgment: credit directly persists an approvals model, reversing the documented app
  dependency before the approval-case engine exists.

## Spec

- Critical: 006F3 found four PostgreSQL tests and executed zero; 006G found its fifth and executed
  zero, despite explicit required acceptance.
- High: the loaded full appraisal response becomes the edit form and is sent on PATCH; response-only
  fields therefore break existing/returned draft saves against the strict backend.
- High: migration 0005 downgrades every state, but repair is draft-only, permanently stranding some
  `review_pending`/`reviewed` rows. It also misses a known returned reason after resubmit.
- Medium: reload clears sanction state and no read returns the pending case UUID required for Epic
  007 navigation.
- Medium: revalidation visibility uses submit-review permission instead of update+risk authority
  and legacy-unverified state.

Summary: Standards found 1 Critical, 3 High, and 3 Medium issues; Spec found 1 Critical, 2 High,
and 2 Medium issues. Each axis's worst issue is the explicitly failed PostgreSQL acceptance.
