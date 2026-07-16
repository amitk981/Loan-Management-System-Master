# Ralph Handoff

## Last Run

2026-07-16_111411_repair

## Current Status

Corrective slice 009B2 is complete. A SAP request becomes `sent` only after the installed public
`sap_workflow.modules.sap_customer_profile` owner decrypts/verifies the retained Annexure-I and the
manual `SapAdapter` accepts its exact plaintext checksum. The frozen assignee receives a governed
task path, can issue/replace a short-lived one-use capability, and downloads the exact workbook
through a nondisclosing audited boundary. No real email or SAP call occurs.

Completed requests now retain a canonical supplied-versus-omitted-aware input digest. New code uses
mandatory `sap.customer_code_created`; reuse uses `sap.customer_code_reused`; create/send/read/
capability/download/denial events freeze safe actor role/team/request/network context without raw
identity, bank, workbook, token, or SAP-code values. Existing normalized global uniqueness, one
active member code, terminal-sanction scope, assignee authority, and zero downstream financial
side effects remain intact.

009C/009D must consume only the immutable public `SapCustomerCodeDecision` containing coherent code,
member, completed request, application, and active-status facts. They must not import Finance SAP
models/modules, adapter/storage internals, delivery capabilities, or SAP exception vocabulary.

## Validation

Run evidence is in `.ralph/runs/2026-07-16_111411_repair/evidence/`. Both exact architecture-review
probes are retained red then green. Django check and migration drift are green; the full backend
suite passed 980 tests with 51 expected skips at 91% coverage. All three PostgreSQL SAP race classes
passed twice. Frontend build, typecheck, lint, and all 322 tests passed. This backend/API slice has no
trusted-browser or screenshot contract.

## Important Continuation Notes

- 009C is sharpened and unblocked. It owns one replay-safe pre-disbursement account under
  `loans.modules.loan_account_lifecycle`; A-121 keeps its Critical permission ungranted and A-122
  keeps all pre-disbursement balances zero. Its optional SAP link must use only the new public
  immutable decision and require exact member/application coherence.
- 009D is sharpened and remains read-only behind 009C. It must consume the 009B2/009C public owner
  seams. Finance initiation and CFC authorization are later actions, not readiness checks.

## Next Run

Run 009C, then 009D.
