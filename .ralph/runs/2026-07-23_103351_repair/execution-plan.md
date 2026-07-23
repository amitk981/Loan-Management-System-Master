# Execution Plan

Selected slice: 011M2-member-portal-kyc-correction-request

## Demonstrated failure

The prior run failed only `agent-declared-result-check.md`. Its review packet already has the exact
`## Result` value, but the packet also contains the phrase `do not commit`, which the authoritative
fast-candidate validator treats as an unmergeable declaration.

## Bounded repair

1. Preserve every product, test, migration, source, and prior-run evidence change in the current
   candidate.
2. Reproduce the exact `ralph_review_packet_declares_ready` failure against the prior run packet.
3. Reword only the prior packet's closing orchestration guidance so it no longer declares
   `do not commit` or `do not merge`.
4. Rerun the same validator until it passes.
5. Complete this repair run's risk assessment, review packet, final summary, and focused evidence,
   with the review packet Result exactly `Ready for independent validation`.
6. Leave full independent revalidation, mechanical bookkeeping, and commit handling to Ralph.

No frontend or backend edit, behavior change, new test, dependency, migration, assumption, or
architecture work is permitted in this repair.
