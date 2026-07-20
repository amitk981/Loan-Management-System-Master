# Risk Assessment

Risk level: High

The preserved 010H3 candidate changes financial-policy immutability, monetary rounding, and atomic
interest reclassification. This repair does not change those production paths; it corrects the
test-storage isolation defect that made independent validation mutate the candidate worktree.

## Repair Controls

- Reproduced the exact recorded candidate hashes: restoring the retained Annexure I fixture changed
  `e8e64bfa...` to `f31b1b5c...`, matching the failed validator byte for byte.
- Added temporary document-storage roots only to test classes that consume the public servicing
  fixture: the 010H3 closure class, its PostgreSQL class, and both interest-rate reverse-consumer
  classes.
- Verified the three-test closure class, one reverse consumer, and the declared five-test PostgreSQL
  class without recreating `sfpcl_credit/local-document-storage`.
- Ran the PostgreSQL class twice; both runs executed exactly five tests and passed.
- Preserved every production model, migration, module, API contract, and source document from the
  original candidate.

## Residual Risk

The full backend suite and coverage remain intentionally delegated to Ralph's independent validator.
The focused repro covers every direct test consumer of `build_servicing_owner_fixture`; the final
frozen-candidate proof still depends on the authoritative full-suite run.

No protected file, dependency, frontend path, external service, or real personal/financial data was
changed or introduced.
