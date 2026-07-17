# Sanitized Disbursement Advice Examples

## Accepted response

```json
{
  "success": true,
  "data": {
    "disbursement_id": "00000000-0000-4000-8000-000000000001",
    "disbursement_advice_communication_id": "00000000-0000-4000-8000-000000000002",
    "delivery_status": "sent",
    "sent_at": "2026-07-17T09:15:00Z"
  }
}
```

Rendered body facts include a synthetic borrower/application/account, decimal amounts, date, and
masked reference `***********9876`; the full UTR and all bank/evidence/internal facts are absent.

## Exact replay

The normalized identical email request returns the exact retained `data` above. Communication,
adapter-call, audit, and workflow counts remain unchanged.

## Changed replay

```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "The disbursement already has different or stale advice evidence."
  }
}
```

## Adapter rejection

```json
{
  "success": false,
  "error": {
    "code": "DELIVERY_FAILED",
    "message": "The disbursement advice was not accepted for delivery."
  }
}
```

The rejected path retains no disbursement advice link, sent communication, advice audit, or advice
workflow event.
