# Review Packet: 2026-07-23_031925_repair

## Result
Ready for independent validation

## Slice
011K-compliance-control-tracker-foundation

## Failure and correction

The complete backend coverage lane failed in
`WitnessEvidenceMigrationTests.test_backfill_is_idempotent_and_reverse_preserves_legacy_rows`
because the new `compliance` graph leaf was included in that test's historical app-state projection.
Its dependency ancestry pulled `applications.Witness` forward past migration `0011`, while the test
database had correctly been reversed to `0011`; the projected model therefore attempted to write the
later `verification_folio_number` column into the older table.

The repair adds only `compliance` to the test's established downstream-owner exclusion set and adds
an assertion that the historical `Witness` projection does not expose the post-0011 field. It does
not change the 011K product candidate, migration graph, or compliance behavior.

## Traceability

The source says compliance must own its control/task/evidence persistence without rewriting facts
owned by earlier modules (`docs/source/codebase-design.md` §19.4 and slice 011K). The product
candidate does that through the new `compliance` owner. This repair keeps the earlier witness
migration proof isolated from later owner leaves, verified by
`WitnessEvidenceMigrationTests` in forward, reverse, idempotency, backfill, and index cases.

## Verification

- Exact RED/GREEN behavior test: reproduced the missing-column error, then passed after the repair.
- Focused migration/compliance pack: 11 tests passed.
- Django system check: passed.
- Migration synchronization (`makemigrations --check --dry-run`): passed with no changes detected.
- Exact complete backend coverage validator: 1,674 tests passed, 171 expected skips, 89% total
  coverage against the 85% floor.
- Diff whitespace check: passed.
- Evidence: `evidence/terminal-logs/01-witness-migration-repro-red.txt` through
  `06-exact-backend-coverage-validator-arm64.txt`.

## Repair environment note

The first exact-validator attempt exposed a Rosetta-only worker architecture mismatch before the
suite could run. The successful rerun used `PYTHONEXECUTABLE` to keep multiprocessing children on
the repository's owner-approved arm64 venv wrapper. No dependency, script, or workflow setting was
modified.

## Recommended Next Action
Run Ralph's independent validation and commit the preserved candidate only if every orchestrator
gate remains green.
