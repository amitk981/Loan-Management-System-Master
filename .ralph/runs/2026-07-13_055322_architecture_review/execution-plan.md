# Execution Plan

Selected slice: architecture-review

1. Pin the review window to `23331d5...955cfc1` and map its four product commits to slices
   `006Z11`, `006Z12`, `007A2`, and `007A3`, their run evidence, epic digests, and cited source
   requirements.
2. Review the range independently on two axes: documented standards/architecture and slice/spec
   fidelity. Inspect production and test hunks, assertions and edge cases, retained red/green,
   PostgreSQL/browser evidence where declared, duplication, module boundaries, and functional
   requirement coverage.
3. Reconcile the prior architecture findings against the corrective implementations. Append a
   newest-first entry to `docs/working/REVIEW_FINDINGS.md`; create or sharpen corrective slices for
   significant new issues, and add an ADR only if the review discovers a durable decision not
   already settled by source documents.
4. Verify `docs/working/CONTEXT.md` against repository reality, audit all `Blocked` slice statuses,
   and confirm the next two `Not Started` slices are concrete and executable from sources already
   opened.
5. Run proportionate documentation/queue and project quality gates, save self-contained evidence,
   then update changed-files, risk, review packet, final summary, Ralph state/progress/handoff, and
   the architecture-review descriptor without modifying production code.
