# Backend-to-Frontend Legacy Register Fixture Trace

Slice: `007T-register-null-contract-and-action-order-closure`

## Authoritative backend shape

`sfpcl_credit/approvals/modules/sanction_register.py::serialize_entry` reads legacy source and
terminal JSON without reconstruction:

- `folio_number` and `loan_type` come from absent legacy borrower/source facts and are `null`.
- `purpose` is `source_facts.get("purpose")` and is therefore top-level `null` when absent.
- `risk` is `source_facts.get("risk")` and is therefore top-level `null` when absent.
- absent/non-list approver facts serialize as `[]`.
- absent terminal `rejection_reason` and `conditions` serialize as `null`.
- empty legacy communication JSON serializes as top-level `null`.

The retained backend integration test
`sfpcl_credit/tests/test_approval_case_routing_api.py::test_legacy_approved_and_rejected_register_rows_are_null_safe`
creates both approved and rejected historical rows without source/terminal facts, mutates current live
member/application values, calls `GET /api/v1/credit-sanction-register/?page=1&page_size=20`, and
asserts the exact values above plus the frozen stored borrower and actor-scoped collection.

## Exact frontend fixture seam

Both `sfpcl-lms/src/pages/registers/RegistersHub.test.tsx` and
`sfpcl-lms/e2e/approval-register-settings.e2e.spec.ts` now pass this wire shape through the public
register UI:

```json
{
  "folio_number": null,
  "loan_type": null,
  "purpose": null,
  "risk": null,
  "approver_names": [],
  "approver_decisions": [],
  "rejection_reason": null,
  "conditions": null,
  "communication": null,
  "exception_reference": null,
  "conflict_abstention_details": [],
  "general_meeting_approval_reference": null
}
```

Every retained non-null stored register field is inherited from the modern fixture. No live member,
application, appraisal, policy, identity, communication, or document request is made to fill the
unavailable values.

## Observable proof

The selected S23 detail remains the existing card/detail composition and displays:

- `Folio number: —`
- `Loan type: —`
- `Purpose: — · —`
- `Risk: —`
- `Approver decisions: —`
- `Communication: —`

The browser contract retains `credit-sanction-register-source-fields.png` and additionally declares
`credit-sanction-register-legacy-null.png` for the exact legacy row. Local Chromium launch is denied
by the macOS Mach-port sandbox; the orchestrator performs the authoritative two independent runs.
