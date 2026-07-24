# Task State and Role Mapping Evidence

| Task type | Open state(s) | Owner | Close proof |
|---|---|---|---|
| completeness_check | application submitted | deputy_manager_finance | leaving submitted |
| appraisal | reference_generated / appraisal draft | deputy_manager_finance | review submission; draft return reopens |
| sanction | sanction submission / pending case | cfo + sanction_committee team | approved/rejected |
| document_verification | checklist in_progress | compliance_team_member + compliance team | checklist advances |
| sap_setup | SAP request draft/sent | senior_manager_finance + treasury | completed |
| disbursement | ready/initiated/pending authorisation | finance stage owner + treasury | CFC/downstream terminal state |
| repayment_posting | SAP posting pending | credit_manager + treasury | posted |
| default_review | grace expired/assessment in progress | credit_manager + credit_assessment | leaves review states |

Executable proof is
`tests.test_workflow_tasks.WorkflowTaskProjectionTests.test_all_eight_task_types_open_once_for_owner_role_and_close_on_exit`.
The exact mapping is also returned by the task module's `task_state_mapping()` interface and
asserted by `test_source_task_state_mapping_exposes_all_eight_owner_rules`.

Idempotency is protected both by projector replay behavior and database partial unique constraint
`uniq_open_workflow_task` over linked entity + task type where status is open.
