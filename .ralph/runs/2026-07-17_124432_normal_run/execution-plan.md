# Execution Plan

Selected slice: 009F2-cfc-authorisation-integrity-and-bank-evidence-closure

1. Inspect the current disbursement aggregate, borrower-bank decision owner, governed source-bank
   owner, loan lifecycle decision, CFC scope/authorisation code, migrations, and focused 009E3/009F
   tests. Confirm the existing public workflow boundary and identify duplicated reconciliation.
2. Add failing-first focused tests for changed borrower-bank evidence, forged later-transfer truth,
   scope/mutation parity, terminal aggregate constraints, governed CFC role variants, replay, and
   PostgreSQL five-caller races. Save the red output under `evidence/terminal-logs/`.
3. Implement one typed initiation/current-CFC evidence decision shared by readiness scope,
   authorisation, and later transfer work. Reconcile exact borrower/source-bank/loan-owner and
   initiation evidence under locks, preserve nondisclosing errors, and keep
   `DisbursementWorkflow` as the sole public mutation owner.
4. Strengthen the disbursement model and one migration with database-valid pending, approved,
   rejected, and transfer-state invariants. Preserve exact replay and immutable audit/workflow/task
   evidence with bounded safe comments and distinct maker/checker.
5. Run focused green tests twice where required, the declared PostgreSQL race tests twice, Django
   check, migration sync, changed-scope lint, and applicable frontend gates. Save all evidence.
6. Review the diff against the slice/source digest, update API/working documentation only if the
   external contract changed, sharpen the next one or two Not Started slices from already-opened
   Epic 009 material, and complete run artifacts, slice status, state, progress, and handoff.

Constraints: no protected or source-document edits; no network installs; backend commands always
use `/Users/amitkallapa/LMS/.ralph/venv/bin/python`; no full backend suite; no git add/commit/push.
