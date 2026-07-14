# 008K API Examples

Representative assertions captured by `test_final_documentation_approval_api.py`.

## Successful checklist item completion

Request: `POST /api/v1/checklist-items/{id}/complete/`

```json
{"loan_document_id":"<uuid>","remarks":"Final checklist verified and attached."}
```

```json
{"success":true,"data":{"checklist_action_id":"<uuid>","entity_type":"checklist_item","entity_id":"<uuid>","previous_status":"pending","new_status":"complete","workflow_event_id":"<uuid>","available_actions":[]}}
```

Exact replay returns the same `checklist_action_id`. Changed remarks return
`409 CHECKLIST_ACTION_CONFLICT` without another action/audit/version/workflow success row.

## Ordered approval

Request: `POST /api/v1/document-checklists/{id}/approve-as-company-secretary/`

```json
{"comments":"All documents verified and attached."}
```

The Credit Manager and Sanction Committee routes return the same durable action shape after their
prerequisites. Credit-before-CS returns `409 CHECKLIST_APPROVAL_OUT_OF_ORDER`.

## Honest disbursement blocker

Request: `POST /api/v1/document-checklists/{id}/sign-disbursement-complete/`

```json
{"comments":"Loan has been disbursed."}
```

```json
{"success":false,"error":{"code":"DISBURSEMENT_EVIDENCE_UNAVAILABLE","message":"A real successful disbursement aggregate is required before this signature."}}
```

The regression asserts zero checklist success writes and retained null loan-account/finance-signature
facts for this response.
