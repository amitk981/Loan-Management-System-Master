# Review Closure Evidence

## Finding Evidence

| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-SEARCH-001 | ROOT-010-GLOBAL-SEARCH-SENSITIVE-AUTHORITY | sfpcl_credit.tests.test_global_search_api.GlobalSearchApiTests.test_cfo_without_blank_cheque_authority_cannot_resolve_owner_by_cheque | evidence/terminal-logs/global-search-authority-red.log | evidence/terminal-logs/global-search-authority-green.log |

## Acceptance Evidence

| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-E10-S1 | sfpcl_credit.tests.test_global_search_api.GlobalSearchApiTests.test_cfo_without_blank_cheque_authority_cannot_resolve_owner_by_cheque | evidence/terminal-logs/global-search-authority-green.log |
| AC-E10-S2 | sfpcl_credit.tests.test_global_search_api.GlobalSearchApiTests.test_application_authority_is_independent_and_scope_precedes_result_cap | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-E10-S3 | sfpcl_credit.tests.test_global_search_api.GlobalSearchApiTests.test_opaque_continuation_replays_pages_without_resubmitting_sensitive_input | evidence/terminal-logs/review-closure-acceptance-green.log |
| AC-E10-S4 | sfpcl_credit.tests.test_global_search_api.GlobalSearchApiTests.test_each_delivered_group_uses_1_20_21_100_101_pagination_contract | evidence/terminal-logs/review-closure-acceptance-green.log |

## Additional Matrix Evidence

- `evidence/terminal-logs/original-reproducer-replay.log` contains the exact original review command,
  a positive pass signal, and exit code 0.
- `evidence/terminal-logs/global-search-client-clearing-red.log` and
  `global-search-client-clearing-green.log` retain the frontend raw-query clearing RED/GREEN cycle.
- `evidence/terminal-logs/global-search-acceptance-matrix.log` covers all 19 permanent backend tests:
  sensitive/input authority, six groups and actions, independent application scope behind 100 denied
  candidates, 1/20/21/100/101 pagination, opaque continuation, validation, and indexed plans.
- `evidence/terminal-logs/frontend-tests.log` covers all 400 frontend regressions.
