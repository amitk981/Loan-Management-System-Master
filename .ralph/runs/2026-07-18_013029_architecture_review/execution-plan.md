# Execution Plan

Selected slice: architecture-review

Run purpose: split oversized slice `009H3` after failed run
`2026-07-18_010406_normal_run` measured 2,195 changed lines against the configured 2,000-line
limit. This architecture-review lane is documentation/state only; production code is out of scope.

1. Read the mandated Ralph context in order, then inspect the complete 009H3 contract, Epic 009
   digest, downstream dependency declarations, and retained failed-run plan, evidence, tests, risk,
   migration manifest, and diff-limit result.
2. Mark 009H3 `Superseded` while retaining its original contract as the traceable parent. Create
   dependency-ordered 009H3A and 009H3B successors, each with the exact origin marker
   `Oversized slice: `009H3`` and a predicted implementation delta comfortably below 2,000 lines.
3. Assign the single state-preserving receipt-owner/outbox migration and provider-identity
   foundation to 009H3A. Assign communications-dispatcher integration, durable pre-dispatch freeze,
   crash recovery, changed-payload conflicts, audit safety, and five-caller race closure to 009H3B.
   Preserve every original requirement, test, evidence obligation, and risk across the pair.
4. Redirect every existing slice dependency on 009H3 to terminal successor 009H3B. Do not sharpen
   or otherwise change unrelated slices.
5. Update only the queue handoff/digest facts needed to make the new order self-contained, plus
   Ralph state/progress and this run's changed-files, risk assessment, review packet, evidence, and
   final summary.
6. Run documentation-only validation: dependency/origin/status checks, JSON validation, protected-
   path inspection, diff-limit accounting, and whitespace checks. Leave commit/merge/push to the
   orchestrator.
