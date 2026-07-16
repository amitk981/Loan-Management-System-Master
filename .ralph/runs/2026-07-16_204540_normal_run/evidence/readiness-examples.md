# Sanitized Readiness Examples

## Genuine owner-backed production state

The public HTTP test creates terminal approval, documentation, signature, physical-security,
verified-bank, SAP-request/code, and loan-account facts through their real owners. With no governed
source bank configured, the response has 22 passes and only:

```json
{
  "code": "source_bank_account_configured",
  "label": "Source bank account configured",
  "status": "fail",
  "reason": "No governed active source bank account is configured."
}
```

When the existing governed source-bank decision seam returns an active decision, the same public
request returns `ready_for_disbursement: true`; all 23 ordered checks are `pass` and contain no
reason. Neither response includes SAP code plaintext, bank account numbers, checksums, storage keys,
capabilities, PAN, or Aadhaar.

## Incomplete state

The incomplete-source public test still returns all 23 ordered checks with safe reasons, an aggregate
false decision, and no audit/workflow changes. Missing and inaccessible loan ids both return the same
`OBJECT_ACCESS_DENIED` envelope.
