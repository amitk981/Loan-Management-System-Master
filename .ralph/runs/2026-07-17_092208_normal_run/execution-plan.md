# Execution Plan

Selected slice: 009E2-disbursement-contract-and-owner-proof-closure

1. Add failing public-interface tests for the exact API §31.2 success shape, §45.2 replay envelope,
   stable §7 blocker/conflict codes, non-empty request/comment-digest evidence, and label-only source
   bank denial. Save the focused RED output.
2. Introduce one governed source-bank configuration lifecycle with an explicit unseeded critical
   permission, immutable activation/version/audit facts, singular current resolution, and safe typed
   decision. Keep raw SFPCL/RBL labels fail-closed and record A-126's unknown provisioner.
3. Replace the private initiation/readiness coupling with a typed initiation decision and a single
   `disbursements.modules.disbursement_workflow` mutation interface. Preserve the public readiness
   projection while retaining exact current owner identities and canonical check digest internally.
4. Make initiation reconcile the typed readiness/source-bank/bank facts, retain generated or supplied
   request identity plus comment digest across row/audit/workflow/task evidence, and reconcile the
   exact success ledger before exposing CFC scope. Preserve manual-bank, lock, race, redaction, and
   zero-later-side-effect invariants.
5. Add genuine owner-backed public success/denial tests and PostgreSQL five-caller acceptance without
   replacing readiness or bank decisions; run focused GREEN tests with the required interpreter and
   save terminal evidence.
6. Update the API contract, assumptions, Epic 009 digest, migration, and Ralph artifacts. Run backend
   check/migration sync plus focused backend tests, then frontend lint/typecheck/tests/build as required;
   do not run the complete backend suite. Review the final diff against source and repository standards.
