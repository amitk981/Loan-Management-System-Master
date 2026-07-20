# Review Packet: 2026-07-20_132000_repair

## Result
Ready for independent validation

## Slice
010E4-rate-effective-date-and-write-boundary-closure

## Recommended Next Action
Run Ralph's full independent validation, including the exact four-test PostgreSQL acceptance class
twice and the complete backend suite under coverage; commit only if every gate passes.

## Demonstrated Failure and Cause

- The prior `review-closure-evidence.md` placed an explanatory due-date projection note directly
  after the Acceptance Evidence table without a peer heading.
- Ralph's exact section parser treated the note as part of Acceptance Evidence and rejected its
  first prose line as a malformed row.
- Once the heading boundary was corrected, the current validator contract also required permanent
  `path.py::Class::method` selectors and explicit `Exit code: 0` markers in retained passing logs.

## Repair

- Added `## Due-Date Projection Note`, ending the machine-readable acceptance section before prose.
- Normalized all finding and acceptance selectors to exact permanent Python test paths and methods.
- Materialized the prior run's genuine RED/GREEN outputs beneath this repair run with selector and
  exit-marker bindings only; no test result or behavior was changed or fabricated.
- Preserved every uncommitted product-code, migration, and permanent-test change from the original
  quarantined implementation.

## Focused Validation

- RED-capable parser loop: `evidence/terminal-logs/closure-parser-red.log` reproduces the exact
  malformed-row failure with exit code 1.
- GREEN parser loop: `evidence/terminal-logs/closure-parser-green.log` reports semantic closure for
  one finding and four acceptance IDs with exit code 0.
- Product code, permanent tests, migrations, slice metadata, source documents, and protected files
  were untouched by this repair. The preserved implementation still requires full independent
  revalidation.

## Reviewer Focus

- Confirm the repair run's closure evidence passes before expensive gates.
- Run the exact declared PostgreSQL acceptance class twice.
- Run complete backend coverage, migration sync, and remaining configured gates before commit.
