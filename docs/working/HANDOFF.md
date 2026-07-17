# Ralph Handoff

## Last Run
2026-07-17_092208_normal_run

## Current Status
009E2 is complete pending independent Ralph validation and commit. Payment initiation now enters
through `disbursements.modules.disbursement_workflow` and consumes one typed readiness decision with
the exact 23-check digest and narrow SAP, borrower-bank, and source-bank governance identities. The
public readiness response remains redacted, while API replay now follows §45.2 and blockers use the
stable §7 vocabulary.

A raw SFPCL/RBL-labelled bank row remains insufficient. One explicit unseeded Critical activation
grant, reason/request evidence, unchanged source facts, and exact version/audit ledgers are required;
A-126's provisioner role remains deliberately unassigned. Initiation freezes a supplied/generated
request id and final-verification comment digest across audit/workflow/task evidence, and CFC scope
reconciles the complete linked ledger. Genuine 008M7/009B3C/009D4 owners reach public initiation;
changed required signers/source-bank facts deny without writes; unrelated signatures remain harmless.
Seventy-four focused backend tests, two real-owner PostgreSQL five-caller races, Django/migration
checks, frontend lint/typecheck/build, and all 327 Vitest tests pass.

## Next Run
Run sharpened 009F CFC authorisation/rejection through the same workflow owner, reconciling 009E2's
request/comment digest and source-bank governance/version/audit identities. Then run sharpened 009G
for unique UTR, evidence, atomic funding, and activation.
