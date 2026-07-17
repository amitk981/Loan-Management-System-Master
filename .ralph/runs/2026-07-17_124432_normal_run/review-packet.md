# Review Packet: 2026-07-17_124432_normal_run

## Result
Complete pending independent orchestrator validation and commit.

## Slice
009F2-cfc-authorisation-integrity-and-bank-evidence-closure

## Outcome
CFC scope and approval/rejection now consume one exact typed current-evidence decision. Initiation
freezes the complete beneficiary-bank and governed source-bank identity manifest; database
constraints prevent incomplete authorisation and pre-approval transfer truth. The external §31.3
request/response and replay contract did not change.

## Traceability

- The source says CFC independently approves/rejects after Senior Manager Finance initiation
  (`integrations.md` §§9.1-9.6; `auth-permissions.md` §§15.7/16.3/26.5). The code enforces active
  governed CFC authority, exact pending relation, and distinct maker/checker; verified by the
  primary/governed/denied actor tests and PostgreSQL races.
- The source says verified beneficiary/source accounts and CFC approval gate disbursement
  (`integrations.md` §§9.4/9.10; `data-model.md` §§12.3/19.3). The application/source owners and
  typed decision fail closed on changed current evidence; verified by the borrower-bank drift and
  source replacement tests.
- The source says models enforce simple persistence invariants and financial workflows use atomic
  locking (`data-model.md` §§28/34; `codebase-design.md` §§6.5/16.4/37.3). The new migration rejects
  partial pending/terminal or pre-approval transfer tuples; verified by the ORM constraint matrix.
- The source requires role/team/request/network/comment audit context without sensitive values
  (`auth-permissions.md` §30). The retained audit binds the exact safe comment digest and decision
  manifest; existing audit/replay corruption tests remain green.

## Verification

- RED: `evidence/terminal-logs/red-authorisation-integrity.txt`
- GREEN focused: `evidence/terminal-logs/focused-authorisation-initiation-green.txt` (33 tests)
- PostgreSQL: `postgresql-cfc-race-1-green.txt` and `postgresql-cfc-race-2-green.txt`
- Static/database: `django-check.txt`, `migration-sync.txt`, `ruff-changed-scope.txt`
- Review manifests: bank/source reconciliation, aggregate constraints, and scope/action parity in
  `evidence/`.

## Review Notes

No frontend, dependency, protected path, source document, or external API contract changed. 009G
was sharpened to consume the named approved typed decision and extend it rather than duplicate the
reconciliation predicates.
