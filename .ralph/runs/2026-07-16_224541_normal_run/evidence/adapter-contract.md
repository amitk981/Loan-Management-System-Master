# Manual / Fake / Future Adapter Contract

One shared test invokes all three adapters through `create_customer_profile_request` and
`get_customer_status`.

- Genuine XLSX package + canonical MIME/name + exact SHA-256 + UUID facts + nonblank key: accepted.
- Exact replay: returns the original immutable result; Future transport call count remains one.
- Changed assignee, file, request key, name, MIME, bytes, or checksum: rejected locally.
- Non-XLSX bytes, including a `PK` lookalike: rejected before Future transport invocation.
- Malformed reference, non-delivered result, or result checksum mismatch: rejected.
- A rejecting Future transport rolls the public send transaction back: the draft request remains
  unmodified and request/code/communication/task/audit/workflow counts remain exact.

Evidence: `terminal-logs/13-red-shared-adapter-contract.txt`,
`terminal-logs/14-green-shared-adapter-contract.txt`,
`terminal-logs/16-expanded-adapter-contract.txt`, and
`terminal-logs/15-current-ledger-and-denial-contract.txt`.
