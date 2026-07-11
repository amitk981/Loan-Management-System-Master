# Sanction Dependency Graph Evidence

Observed production business-app direction:

`approvals.modules.sanction_handoff -> credit.modules.appraisal_workflow`

- Forbidden `credit -> approvals` references: 0
- Forbidden `approvals -> credit` references: 0
- Required public approvals-to-credit handoff observed: yes
- Public credit allowlist: `sfpcl_credit.credit.modules.appraisal_workflow`

The repository assertion producing this result is
`SanctionSubmissionApiTests.test_business_app_dependency_direction_is_approvals_to_credit_only`.
