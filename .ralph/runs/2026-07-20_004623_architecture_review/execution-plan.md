# Execution Plan

Selected slice: `architecture-review`

## Boundary

- Treat `0b5be35c` as the fixed point: it is the post-Epic-009-finalizer Ralph semantic-review
  enforcement baseline, immediately before the four product slices counted by the current cadence.
- Review product commits `dc666672`, `41f3034d`, `bdae40f4`, and `6883816b` (010A-010D).
- Exclude mechanical run/state/progress/handoff artifacts from product criticism except where they
  provide validation evidence. Do not modify production code or protected files.

## Review Work

1. Read the four selected slice contracts, their Epic 010 digest sections and cited source facts,
   plus the slice-owned test and validation evidence.
2. Run independent Standards and Spec review passes over `git diff 0b5be35c...HEAD`, then reconcile
   them with direct inspection of the changed models, migrations, services, views, routes, and tests.
3. Critique assertion quality and edge cases; check source-contract fidelity, API and transaction
   boundaries, financial/data integrity, duplicated rules, ownership seams, and architecture drift.
4. Use focused read-only probes or tests only when static inspection cannot establish a finding.
   Retain any finding/closure reproducer under this run's `evidence/` tree with stable IDs.
5. Check Epic 010 requirement-ID traceability, `CONTEXT.md` truthfulness, and whether any Blocked
   slice has stale prerequisites.

## Deliverables

- Update only stable finding-ID sections in `docs/working/REVIEW_FINDINGS.md` when the review finds
  a new, carried, or closed finding. Add a grouped numeric corrective slice only for a new open
  Critical/High root that has no actionable existing owner.
- Complete `risk-assessment.md`, `review-packet.md`, and `final-summary.md`; include exact convergence
  metrics and exactly one semantic Finding Closure Manifest.
- Run documentation-scope, manifest, queue, and artifact checks available without changing Ralph
  orchestration. Set the packet Result exactly to `Ready for independent validation` only after the
  review artifacts and evidence are internally consistent.
