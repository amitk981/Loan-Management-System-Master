# Review Closure Evidence

## Finding Evidence
| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-INTEREST-001 | ROOT-010-INTEREST-CALCULATION-OWNER | sfpcl_credit.tests.test_interest_policy_integrity_closure.InterestPolicyIntegrityClosureTests.test_approved_policy_is_immutable_before_consumption_and_amends_by_version | evidence/terminal-logs/interest-policy-immutability-red.log | evidence/terminal-logs/interest-closure-focused-green.log |

## Acceptance Evidence
| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-INT3-1 | sfpcl_credit.tests.test_interest_policy_integrity_closure.InterestPolicyIntegrityClosureTests.test_approved_policy_is_immutable_before_consumption_and_amends_by_version | evidence/terminal-logs/interest-closure-focused-green.log |
| AC-INT3-2 | sfpcl_credit.tests.test_interest_policy_integrity_closure.InterestPolicyIntegrityClosureTests.test_approved_policy_rounds_once_after_multi_segment_half_unit_decision | evidence/terminal-logs/interest-closure-focused-green.log |
| AC-INT3-3 | sfpcl_credit.tests.test_interest_capitalisation_api.InterestCapitalisationApiTests.test_mismatched_account_interest_rejects_every_capitalisation_side_effect | evidence/terminal-logs/interest-closure-focused-green.log |
| AC-INT3-4 | sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestPolicyIntegrityPostgreSQLAcceptanceTests.test_exact_capitalisation_race_replays_one_byte_stable_decision | evidence/terminal-logs/interest-policy-postgresql-pass-1.log |
| AC-INT3-5 | sfpcl_credit.tests.test_servicing_postgresql_acceptance.InterestPolicyIntegrityPostgreSQLAcceptanceTests.test_changed_key_capitalisation_race_retains_one_reclassification | evidence/terminal-logs/interest-policy-postgresql-pass-2.log |

The PostgreSQL evidence files each contain the complete declared five-test class. The focused
capitalisation suite additionally covers exact success and separate account, schedule, ledger, and
payment-owner mismatch matrices with retained zero-side-effect assertions.
