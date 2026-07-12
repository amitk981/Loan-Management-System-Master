# Synthetic API examples

`POST /api/v1/members/` accepts synthetic individual/FPC §13.2 payloads and returns the canonical
member UUID, masked PAN/Aadhaar, `version: 1`, and six-field member actions in the standard envelope.

`PATCH /api/v1/members/{member_id}/` with `{"email":"updated@example.test","version":1}` returns
the updated canonical member and increments `version`; a stale version returns `409 STALE_WRITE`.

Verified identity PATCH with `{"pan":"PQRST6789U","version":1}` returns
`409 VERIFIED_IDENTITY_LOCKED`. The reasoned synthetic correction uses
`POST /api/v1/members/{member_id}/reverification/` with
`{"pan":"PQRST6789U","reason":"Synthetic correction evidence","version":1}` and returns KYC
`pending`; stored history contains only the masked PAN.
