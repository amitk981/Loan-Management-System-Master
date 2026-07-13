# Credit action/write matrix

All rows use the six-field production `available_actions` projection and the matching public module
write. `enabled` rows commit once; denied rows preserve the resource and all evidence cardinalities.

| Action | Executed variants | Public write | Result |
|---|---|---|---|
| `credit.eligibility.run` | enabled, permission, state, stale state, object scope | `EligibilityAssessmentModule.run` | exact projected state/permission reasons; stale/scope category; zero loser evidence |
| `credit.loan_limit.calculate` | enabled, permission, state, stale state, object scope | `LoanLimitCalculator.calculate_for_application` | exact state/permission reasons; immutable assessment on denial |
| `credit.appraisal.create` | enabled, permission, state, object scope | `AppraisalWorkflow.create_or_update(partial=False)` | exact eligibility/authority reason; no partial risk/appraisal evidence |
| `credit.appraisal.update` | enabled, permission, state, object scope | `AppraisalWorkflow.create_or_update(partial=True)` | draft-only parity; frozen draft on denial |
| `revalidate_appraisal_prerequisites` | enabled, permission, state, provenance, object scope | `AppraisalWorkflow.revalidate_prerequisites` | exact governed-repair reason; no remediation evidence on denial |
| `credit.appraisal.submit_review` | enabled, permission, state, provenance, object scope | `AppraisalWorkflow.submit_for_review` | exact state/provenance reason; no review evidence on denial |
| `credit.appraisal.review` | reviewed/returned/rejected success; permission, role, object scope, maker-checker, state, provenance, malformed rejection | `AppraisalWorkflow.review` | one decision per success, one rejection note only for rejection, zero denied evidence |
| `credit.appraisal.submit_sanction` | enabled, permission, role, object scope, state, provenance, immutable review, stale state | `SanctionHandoffModule.submit_reviewed_appraisal` | one linked case/event on success; zero case or loser evidence on denial |

PostgreSQL acceptance: both `postgresql-five-race-run-1.log` and
`postgresql-five-race-run-2.log` found five tests, ran without skips, and preserved one valid winner
with no loser evidence. The stale-enabled sanction projection is asserted before the competing
public submissions in the unchanged authoritative race.
