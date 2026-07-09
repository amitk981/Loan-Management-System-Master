# Risk Assessment

Risk level: High

Selected slice: `004I-sensitive-masking-and-reveal-audit`

## Why High
- The slice exposes full PAN/Aadhaar values in a controlled path.
- It touches field-level RBAC, audit logging, and frontend handling of sensitive data.
- A regression could leak identity values through API responses, audit metadata, browser storage, or
  unauthorised roles.

## Controls Applied
- Implemented only member `pan` and `aadhaar` reveal; nominee, witness, signatory, document, export,
  generic sensitive reveal, and bank-account reveal are deferred.
- Required base `members.member.read` plus exact field permission
  `members.sensitive.reveal_pan` or `members.sensitive.reveal_aadhaar`.
- Full values are returned only in the immediate success response, with `Cache-Control: no-store`,
  `Pragma: no-cache`, and a five-minute `expires_at`.
- Audit logs store metadata only. Tests assert full PAN/Aadhaar, hashes, and token field names are
  absent from success and denial audit metadata.
- Frontend reveal controls require a reason, clear the reason after success, and keep full values
  only in component state. No local storage, mock data, or URL persistence was added.
- No database schema change or plaintext columns were introduced.

## Residual Risk
- The current protected/encrypted member fields are still represented by test/dev token strings in
  the existing prototype storage model; real cryptographic storage remains a broader platform
  hardening concern outside this slice.
- Live screenshot capture was not possible in this sandbox because localhost binding failed and the
  in-app browser was unavailable. Static visual HTML evidence is saved, and frontend behavior is
  covered by vitest/typecheck/build.

Manual review required: normal High-risk review recommended, but standing approval permits
orchestrator validation and commit if all gates pass.
