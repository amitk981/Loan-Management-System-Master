# Risk Assessment

Risk: Medium

- Database: one additive witness table with protected FKs and indexed identity hashes; no rewrite.
- Privacy: PAN/Aadhaar use protected tokens/hashes and masked responses. Tests exclude plaintext,
  tokens, and hashes from audit JSON.
- Authorization: atomic witness permissions are role-limited and combined with application object
  access. A-062 records the source catalogue omission.
- Workflow: verification derives from persisted member/KYC/shareholding facts. Creation writes one
  audit row and changes no application state or workflow event.
- Residual: governance may later rename the endpoint/permissions or refine shareholder
  qualification; the nested interface can be versioned without rewriting stored evidence.

Standing approval applies; no veto or protected-path modification was found.
