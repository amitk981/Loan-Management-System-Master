# Review Packet: 2026-07-20_064142_repair

## Result
Ready for independent validation

## Slice
010E3-servicing-financial-owner-and-replay-convergence

## Recommended Next Action
Run Ralph's full independent validation, including the declared five-test PostgreSQL acceptance
twice and the complete backend suite under coverage; commit only if every gate passes.

## Demonstrated Failure and Cause

- The prior `review-closure-evidence.md` placed an explanatory PostgreSQL note directly after the
  Acceptance Evidence table without a peer heading.
- Ralph's exact section parser correctly treated that note as part of Acceptance Evidence and
  rejected its first prose line as a malformed row.
- Once that boundary was repaired, the parser exposed dotted Django labels that did not meet the
  file-bound exact-selector contract. This was another defect in the same machine-readable
  evidence artifact, not a product implementation failure.

## Repair

- Added `## PostgreSQL Acceptance Note`, ending the machine-readable acceptance section before the
  prose.
- Normalized every finding and acceptance selector to `path.py::Class::method`.
- Retained the original genuine RED/GREEN logs in the repair run and added exact permanent-selector
  bindings; no test result or product behavior was changed.

## Focused Validation

- RED-capable parser loop: `evidence/terminal-logs/closure-parser-red.log` reproduces the exact
  malformed-row failure with exit code 1.
- GREEN parser loop: `evidence/terminal-logs/closure-parser-green.log` reports semantic closure for
  5 findings and 7 acceptance IDs with exit code 0.
- Product code, permanent tests, migrations, slice metadata, and protected files were untouched by
  this repair. The preserved implementation still requires complete independent revalidation.

## Reviewer Focus

- Confirm the repair run's closure evidence passes before expensive gates.
- Run the exact declared PostgreSQL acceptance class twice.
- Run complete backend coverage, migration sync, and remaining configured gates before commit.
