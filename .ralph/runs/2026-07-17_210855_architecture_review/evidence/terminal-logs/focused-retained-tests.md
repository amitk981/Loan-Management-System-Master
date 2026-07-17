# Focused retained tests

Command used the mandated backend interpreter and ran the field-encryption module plus one retained
rollback, transfer-replay, and post-disbursement-signature test.

```text
Found 10 test(s).
System check identified no issues (0 silenced).
test_fresh_adapter_retry_reuses_provider_receipt_after_post_acceptance_rollback ... ok
test_replay_rejects_changed_register_and_pending_advice_relations ... ok
test_public_post_disbursement_signature_binds_current_transfer_evidence ... ok
test_canonical_ciphertext_tamper_is_rejected_by_authentication ... ok
test_missing_dedicated_keys_never_fall_back_to_django_secret_key ... ok
test_noncanonical_base64_tamper_is_rejected_as_malformed ... ok
test_previous_key_remains_readable_during_rotation ... ok
test_random_ciphertext_and_field_specific_hashes_do_not_expose_plaintext ... ok
test_round_trip_is_versioned_field_bound_and_lookup_hash_is_stable ... ok
test_wrong_key_and_inactive_version_fail_closed ... ok

Ran 10 tests in 2.056s
OK
```

Exit status: `0`. This confirms the reviewed retained tests are green; the RED probes demonstrate
contract edges those tests do not cover.
