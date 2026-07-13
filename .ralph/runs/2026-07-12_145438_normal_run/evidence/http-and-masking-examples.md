# HTTP and Masking Examples

Object-denied checker projection:

```json
{"action_code":"members.member.identity_change.approve","label":"Approve identity change","enabled":false,"disabled_reason":"You cannot access this member.","required_permission":"members.member.identity_change.approve","required_role":null}
```

The matching approval POST is translated to HTTP 403 `FORBIDDEN` with the same message and creates
zero history/audit rows. Concurrent identity duplicates are translated to HTTP-compatible
`400 VALIDATION_ERROR` field facts such as `{"pan":"A member with this PAN already exists."}`.

Protected history examples retain masked tokens only (for example `******6789`); plaintext PAN,
Aadhaar, encrypted token contents, and keyed hashes are absent from response/history/audit evidence.
