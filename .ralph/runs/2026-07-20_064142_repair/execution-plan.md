# Execution Plan

Selected slice: 010E3-servicing-financial-owner-and-replay-convergence

## Demonstrated failure

Independent validation stopped before product gates because the prior run's
`review-closure-evidence.md` left a PostgreSQL explanatory note inside the exact
`## Acceptance Evidence` section. The semantic-closure parser consequently treated the note's
first line as a malformed table row.

## Repair boundary

- Preserve every existing production-code, test, and RED/GREEN evidence change.
- Add a peer Markdown heading before the PostgreSQL note so the acceptance section contains only
  its exact table.
- Materialize the corrected closure artifact and its already-retained evidence in this repair run
  directory if repair validation consumes the current run as its evidence root.
- Do not change product code, tests, slice contracts, source documents, or protected workflow files.

## Feedback loop and verification

1. Reproduce the malformed-row signal with the exact Ralph semantic-closure parser.
2. Apply only the section-boundary correction.
3. Re-run the semantic-closure parser and require its positive five-finding/seven-acceptance result.
4. Save the focused repair result, honest risk assessment, review packet, and final summary.
5. Finish with `review-packet.md` Result exactly `Ready for independent validation`; the
   orchestrator owns full PostgreSQL and complete-suite revalidation.
