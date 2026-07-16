# Ralph Handoff

## Last Run

2026-07-16_172426_repair

## Current Status

008M5's trusted-browser launch repair is complete pending independent orchestrator revalidation.
Staff signed-copy uploads and re-uploads now form an immutable legal-owner succession chain while
the generated renderer original remains unchanged. Correction and final-return actions are durable,
visible after refetch, and block item completion or ordered approvals until an exact signed successor
resolves them. Conditions are retained and shown against the exact approval role.

A-125 remains honest: production queue and detail projections expose
`governed_attorney_unconfigured`, issue no PoA create command, and grant no attorney authority. The
future governed decision is injected through the security-owner gateway; stale and wrong-role paths
remain zero-write, and the decision identity participates in the opaque action identity.

## Validation

Failing-first and green evidence is in
`.ralph/runs/2026-07-16_165237_normal_run/evidence/terminal-logs/`. The final impacted backend run
passed 49 tests with two expected PostgreSQL-only skips; the durable public matrix and copied review
probes pass. Frontend documentation tests pass (18), as do typecheck, lint, build, Django check, and
migration sync. The repair keeps the Playwright bundled browser as first choice and uses the host's
installed Google Chrome only when that bundle is absent. Playwright collects the exact real-Django
spec and five screenshot names; the focused frontend tests, typecheck, lint, and build pass. The
coding sandbox terminated host Chrome during macOS service bootstrap, so the orchestrator must run
the declared browser contract twice outside that sandbox and retain the screenshots.

Independent Standards and Spec reviews initially found response-schema, replay, blocker-surface,
condition-stage, attorney-gateway, browser-order, and matrix gaps. All were repaired; both final
re-reviews report no remaining finding.

## Important Continuation Notes

- The one new migration is `legal_documents.0014`; it creates only the two immutable staff legal
  evidence tables and preserves existing document/checklist/security rows.
- Oversized slice 009B3 is superseded by 009B3A (non-destructive model ownership) and 009B3B
  (executable policy/adapter dependency closure); both preserve its full requirements while staying
  independently executable below the 2,000-line limit.
- 009D2 must consume the post-009B3B SAP owner and exact current legal/security evidence. 009E remains
  blocked behind 009D2.

## Next Run

Run 009B3A, then 009B3B, then 009D2. Proceed to 009E only after all corrective gates pass.
