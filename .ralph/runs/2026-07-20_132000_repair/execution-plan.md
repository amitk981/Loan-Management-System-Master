# Execution Plan

Selected slice: 010E4-rate-effective-date-and-write-boundary-closure

## Demonstrated failure

Independent validation stopped before product gates because the prior run's
`review-closure-evidence.md` left an explanatory due-date projection note directly inside the exact
`## Acceptance Evidence` section. Ralph's semantic-closure parser therefore treated the note's
first line as a malformed table row.

## Repair boundary

- Preserve every uncommitted production-code, migration, permanent-test, and RED/GREEN evidence
  change from the quarantined 010E4 implementation.
- End the machine-readable Acceptance Evidence section with a peer Markdown heading before the
  explanatory note.
- Materialize the corrected closure artifact and its retained evidence beneath this repair run,
  because semantic validation resolves evidence from the current run directory.
- Normalize test references to Ralph's required `path.py::Class::method` selectors if the corrected
  section boundary exposes that progressive artifact defect.
- Do not change product code, tests, slice/source contracts, protected workflow files, or business
  behavior.

## Feedback loop and verification

1. Reproduce the prior malformed-row signal with Ralph's exact semantic-closure validator.
2. Apply only the evidence-section and exact-selector corrections the validator demonstrates.
3. Re-run the same validator against this repair run and require a positive one-finding/four-
   acceptance result with exit code 0.
4. Save the focused RED/GREEN parser logs, risk assessment, review packet, and final summary.
5. Finish with `review-packet.md` Result exactly `Ready for independent validation`; the
   orchestrator owns full PostgreSQL and complete-suite revalidation.
