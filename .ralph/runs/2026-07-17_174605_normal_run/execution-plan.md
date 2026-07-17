# Execution Plan

Selected slice: CR-009-deterministic-field-encryption-tamper-coverage

1. Keep the change at the existing `FieldEncryption` interface seam: production encryption,
   models, services, endpoints, masking, and key policy remain untouched.
2. In `test_field_encryption.py`, introduce one test-harness helper that deterministically makes a
   Base64 spelling noncanonical and one that deterministically changes decoded ciphertext while
   preserving canonical Base64.
3. Follow a vertical RED/GREEN cycle: first add one focused behavior test that references the
   absent helpers and save the expected failure; then add the minimal helpers and split the old
   combined tamper test so each rejection branch has an exact `InvalidCiphertext` message assertion.
4. Preserve the existing wrong-key and inactive-key-version assertions in a separately named test.
5. Run the focused test module repeatedly with the mandated backend interpreter, retaining per-run
   coverage JSON and a comparison proving identical executed/missing line sets for
   `shared/encryption.py`.
6. Run scoped Django check/migration-sync and the applicable frontend gates, then review the diff
   for production-code absence and slice-only scope.
7. Save terminal evidence, changed-files, risk assessment, review packet, and final summary; mark
   the selected slice complete and update Ralph state/progress/handoff. Sharpen the next one or two
   Not Started slices only if the source/digests already opened during this run provide concrete
   additional requirements.
