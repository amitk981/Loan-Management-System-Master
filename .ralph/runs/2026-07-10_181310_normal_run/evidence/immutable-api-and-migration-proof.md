# Immutable Appraisal API and Migration Proof

## Create/read projection

The public API test creates a draft with synthetic appraisal facts and receives both canonical
prerequisite projections. The relevant response shape is:

```json
{
  "eligibility_assessment_id": "same-uuid-before-and-after-rerun",
  "loan_limit_assessment_id": "same-uuid-before-and-after-rerun",
  "prerequisite_provenance": "verified",
  "eligibility_snapshot": {
    "member_active_check": "pass",
    "default_check": "no_default",
    "document_check": "complete",
    "terms_acceptance_check": "accepted",
    "purpose_check": "agriculture_aligned",
    "nominee_check": "valid",
    "overall_result": "eligible",
    "assessed_by_user_id": "synthetic-user-uuid",
    "assessed_at": "2026-07-10T12:00:00+05:30"
  },
  "loan_limit_snapshot": {
    "land_area_acres": "20.00",
    "shareholding_based_limit_amount": "500000.00",
    "land_based_limit_amount": "500000.00",
    "final_eligible_loan_amount": "500000.00",
    "requested_amount": "400000.00",
    "amount_within_limit_flag": true,
    "exception_required_flag": false,
    "calculation_rule_version": "loan-policy-v1.0",
    "configuration_source": {
      "type": "loan_policy_config",
      "loan_policy_config_id": null,
      "policy_name": null,
      "board_approval_reference": null
    }
  },
  "repayment_capacity_notes": "Seasonal crop proceeds cover the proposed repayment schedule."
}
```

The test then replaces the current eligibility result with `ineligible/default_found` and the
current same-UUID loan-limit amount with `700000.00`. A second appraisal GET remains byte-for-byte
equal for both frozen projections. PATCH of `recommended_amount = 600000.00` is rejected against
the frozen `500000.00` boundary even though the mutable current assessment would allow it.

Evidence: `terminal-logs/appraisal-edge-cases-green.log` and
`terminal-logs/final-focused-backend.log`.

## Submit reason redaction

Submit stores `Appraisal completed for Credit Manager review.` in the appraisal-owned
`submission_remarks` field. Its audit JSON contains only:

```json
{
  "appraisal_status": "review_pending",
  "submission_reason_exists": true,
  "submission_reason_owner_id": "synthetic-appraisal-uuid"
}
```

The free text is absent from audit/workflow evidence.

## Legacy migration

The migration test creates two pre-006E2 appraisals. The safe row has assessment timestamps before
appraisal creation and no later success audit; it becomes `verified` with complete projections.
The ambiguous row has a later `loan_limit.calculated` audit and remains `legacy_unverified` with
empty projections. It cannot submit until the authorised draft-only revalidation action succeeds.

Evidence: `terminal-logs/legacy-migration-proof.log` and
`terminal-logs/tdd-green-legacy-revalidation.log`.
