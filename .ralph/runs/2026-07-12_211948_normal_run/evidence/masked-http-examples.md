# Masked HTTP Examples

## Canonical member readback

```json
{
  "success": true,
  "data": {
    "member_id": "member-1",
    "member_type": "producer_institution",
    "pan": { "masked": "******234F", "can_view_full": false },
    "aadhaar": { "masked": "********1234", "can_view_full": false }
  }
}
```

## Authoritative stale-write failure

```json
{
  "success": false,
  "error": {
    "code": "STALE_WRITE",
    "message": "Version 7 is stale; current member version is 8."
  }
}
```

These are synthetic, masked examples matching the mounted transport assertions; no plaintext identity
values are retained in this evidence artifact.
