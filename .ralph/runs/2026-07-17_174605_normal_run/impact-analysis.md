# Impact Analysis

Slice: `CR-009-deterministic-field-encryption-tamper-coverage`

## Change boundary

This is a test-determinism correction. The permitted change is confined to
`sfpcl_credit/tests/test_field_encryption.py`; `sfpcl_credit/shared/encryption.py` and every
production caller remain unchanged. The regression will exercise the existing `FieldEncryption`
interface with two explicit mutations: noncanonical Base64 and canonical authenticated-ciphertext
tampering.

## Backend impact and grep evidence

- Shared module under test: `sfpcl_credit/shared/encryption.py` defines `FieldEncryption` and
  `InvalidCiphertext`. Its `_parse` method maps Base64 decode/canonicalization errors to
  `Ciphertext is malformed`, while `decrypt` maps AES-GCM tag failure to
  `Ciphertext authentication failed` (`rg -n "FieldEncryption|InvalidCiphertext|_unb64"`).
- Models storing values produced by the interface, but not changed by this slice:
  `security_instruments.CDSLSharePledge` stores pledgor/pledgee BO ciphertext,
  `security_instruments.BlankDatedCheque` stores cheque-number ciphertext, and
  `sap_workflow.SAPCustomerProfileRequest` stores PAN/Aadhaar ciphertext
  (`rg -n "encrypted" sfpcl_credit/security_instruments/models.py sfpcl_credit/sap_workflow/models.py`).
- Production modules consuming the interface, but not changed by this slice:
  `security_instruments/modules/cdsl_share_pledge.py`,
  `security_instruments/modules/blank_dated_cheque.py`,
  `documents/modules/sensitive_data_access.py`,
  `sap_workflow/modules/sap_customer_request.py`, and
  `sap_workflow/modules/annexure_storage.py`
  (`rg -n "FieldEncryption" sfpcl_credit --glob '*.py'`).
- HTTP boundaries transitively backed by those consumers, but with no contract or code change:
  blank-cheque create/update/reveal, CDSL pledge create/detail/reveal, SAP customer-profile
  request/send/complete, and Annexure-I capability/download routes in
  `sfpcl_credit/config/urls.py` (`rg -n "cdsl|blank.cheque|sap.customer|annexure"`).
- No migration, settings, key-policy, masking, reveal-policy, endpoint, serializer, or public API
  change is required.

## Frontend impact

None. No screen, component, route, type, transport, label, layout, or styling changes. The binding
`FRONTEND_DESIGN_RULES.md` therefore requires no UI work or visual evidence.

## Blast radius and regression ownership

- Directly affected module: the field-encryption test module only. Add focused regressions there
  for deterministic noncanonical Base64 rejection and deterministic canonical AES-GCM tamper
  rejection, while retaining wrong-key and inactive-version coverage.
- Other backend consumers listed above use the unchanged production interface and have no changed
  behavior. Their existing API regressions remain the cross-module safety net:
  `test_blank_dated_cheque_api.py`, `test_final_documentation_approval_api.py`, and
  `test_sap_customer_profile_request_api.py` all call `FieldEncryption` directly. No new test in
  those modules is justified because the defect is solely in the shared test's random mutation,
  not in their behavior.
- `test_field_encryption.py` is the only existing test that directly asserts
  `InvalidCiphertext` for this token parser. It receives all new regression cases, satisfying the
  per-affected-module requirement without duplicating parser-branch assertions in endpoint suites.

## Verification plan

1. Capture RED from a focused regression that names deterministic mutation helpers before those
   helpers exist.
2. Implement only the test helpers/cases; do not edit production encryption code.
3. Run the focused module repeatedly under coverage and compare exact executed-line sets.
4. Run Django check and migration-sync plus the directly affected backend module. Do not run the
   complete backend suite; the orchestrator owns that authoritative gate.
5. Run unchanged frontend lint, tests, typecheck, and build as the repository-wide regression gate.
