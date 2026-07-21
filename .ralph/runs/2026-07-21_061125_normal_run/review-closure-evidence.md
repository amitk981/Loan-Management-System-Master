# Review Closure Evidence

## Finding Evidence
| Finding ID | Root ID | Permanent Test | RED Evidence | GREEN Evidence |
|---|---|---|---|---|
| AR-010-DPD-001 | ROOT-010-DPD-SNAPSHOT-OWNER | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_dpd_database_and_policy_owner | evidence/terminal-logs/dpd-owner-red.log | evidence/terminal-logs/servicing-asof-focused.log |
| AR-010-REMINDER-001 | ROOT-010-REMINDER-DELIVERY-OWNER | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_reminder_provider_boundary_rechecks_serviceability | evidence/terminal-logs/reminder-owner-red.log | evidence/terminal-logs/servicing-asof-focused.log |
| AR-010-MIS-001 | ROOT-010-MIS-AS-OF-OWNER | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_mis_replay_and_cutoff_owner | evidence/terminal-logs/mis-owner-red.log | evidence/terminal-logs/servicing-asof-focused.log |

## Acceptance Evidence
| Acceptance ID | Test | Evidence |
|---|---|---|
| AC-SAO-1 | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_dpd_database_and_policy_owner | evidence/terminal-logs/servicing-asof-focused.log |
| AC-SAO-2 | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_capitalisation_is_classified_once | evidence/terminal-logs/servicing-asof-focused.log |
| AC-SAO-3 | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_reminder_provider_boundary_rechecks_serviceability | evidence/terminal-logs/servicing-asof-focused.log |
| AC-SAO-4 | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_mis_replay_and_cutoff_owner | evidence/terminal-logs/servicing-asof-focused.log |
| AC-SAO-5 | sfpcl_credit/tests/test_servicing_as_of_owner_boundary.py::ServicingAsOfOwnerBoundaryTests::test_batch_continuation_contract | evidence/terminal-logs/servicing-asof-focused.log |

