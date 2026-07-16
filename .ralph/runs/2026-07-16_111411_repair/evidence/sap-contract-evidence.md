# 009B2 SAP Contract Evidence

## Failing-first review probes

- `evidence/terminal-logs/sap-contract-red.log` captures both architecture-review defects before
  implementation: the assignee capability endpoint returned HTTP 404, and a reused-code completion
  with newly supplied optional values returned HTTP 200 instead of 409.
- The same two exact seams are retained as
  `SapCustomerProfileRepairTests.test_sent_assignee_reads_exact_retained_workbook_through_delivery_capability`
  and `test_reuse_changed_optional_payload_conflicts_without_loser_artifacts`.

## Green contract

- `evidence/terminal-logs/sap-contract-green.log` records 51 green SAP tests, including exact
  decrypted workbook equality, plaintext checksum equality, encrypted physical storage inherited
  from 009A, one-use/expiry/tamper/replacement, cross-user/request/application/file denial, exact
  supplied-versus-omitted replay, secret scans, and zero loser success ledgers.
- `evidence/terminal-logs/009b2-postgresql-races-1.log` and `-2.log` retain two independent
  PostgreSQL passes of the request/code/member winner-loser races after the owner transfer.

## Sanitized public examples

Send returns a retained delivery projection (representative identifiers only):

```json
{
  "request_status": "sent",
  "delivery": {
    "delivery_reference": "manual:<opaque-id>",
    "checksum_sha256": "<plaintext-workbook-sha256>",
    "document_id": "<restricted-document-id>",
    "capability_path": "/api/v1/sap-customer-profile-requests/<request-id>/annexure-i-delivery-capability/"
  }
}
```

Capability issue returns only the delivery identity, checksum, one signed one-use token, and expiry.
The governed GET returns the exact retained XLSX bytes, consumes that version, and writes one
`sap.annexure_i_downloaded` event. Tokens are absent from communication, workflow, and audit facts.

Completion success emits exactly one of:

```json
{"action": "sap.customer_code_created", "outcome": "created", "reuse": false}
{"action": "sap.customer_code_reused", "outcome": "reused", "reuse": true}
```

Every SAP create/send/complete/code-read/capability/download/denial audit freezes safe actor user and
type, role/team codes, entity, old/new state, request id, IP, user agent, timestamp, reason, and
outcome. Regression scans reject PAN, Aadhaar, address, bank, workbook, token, and raw SAP-code text.

## Ownership and migration

- `sfpcl_credit.sap_workflow.modules.sap_customer_profile` is the installed public workflow owner.
  HTTP and downstream dependency guards reject private Finance SAP imports; the owner returns the
  immutable `SapCustomerCodeDecision` required by 009C/009D.
- Manual and fake adapters satisfy the same `SapAdapter` method contract. The manual adapter accepts
  exact bytes/checksum and performs no real email/SAP call.
- `finance.0003_sap_delivery_replay_contract` adds only compatibility fields to the retained applied
  SAP request table, so existing row/table identities are not duplicated or transferred.
- `evidence/terminal-logs/migration-check-focused.log` records `No changes detected`.
