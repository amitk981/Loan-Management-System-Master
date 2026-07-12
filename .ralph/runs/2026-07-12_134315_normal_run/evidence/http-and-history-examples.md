# Witness API and history evidence

Representative tested create fields:

```json
{"member_id":"<member-uuid>","witness_name":"Sita Patil","address":"Village Road, Pune","mobile":"9876543210","pan":"<valid-pan>","aadhaar":"<valid-aadhaar>"}
```

Representative tested contact correction:

```json
{"version":1,"address":"Market Road, Pune","mobile":"9123456780"}
```

Persisted history assertions:

```json
{"changed_fields":["address","mobile"],"old":{"address":"Village Road, Pune","mobile":"9876543210"},"new":{"address":"Market Road, Pune","mobile":"9123456780"}}
```

Representative denied update action asserted by backend and mounted frontend tests:

```json
{"action_code":"update","label":"Correct Witness","enabled":false,"disabled_reason":"Missing witness update permission.","required_permission":"members.witness.update","required_role":null}
```

PAN/Aadhaar examples are intentionally placeholders here; the tests assert full submitted values do
not appear in responses, history, or correction audit JSON.
