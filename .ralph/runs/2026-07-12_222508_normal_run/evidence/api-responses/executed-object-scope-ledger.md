# Executed Object-Scope Ledger

Focused command: `manage.py test sfpcl_credit.tests.test_credit_action_parity_matrix -v 2`

Every result below was appended only after its row helper executed the exact six-field disabled
projection assertion, observed the matching public write's object-access exception, asserted
`OBJECT_ACCESS_DENIED`, and compared the complete persisted before/after snapshot.

| Action code | Projection | Public write | Category | Evidence |
|---|---|---|---|---|
| `credit.eligibility.run` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `credit.loan_limit.calculate` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `credit.appraisal.create` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `credit.appraisal.update` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `revalidate_appraisal_prerequisites` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `credit.appraisal.submit_review` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `credit.appraisal.review` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |
| `credit.appraisal.submit_sanction` | pass | denied | `OBJECT_ACCESS_DENIED` | unchanged |

All disabled reasons were exactly: `You do not have access to this loan application.`

The ledger assertion requires this exact set and cardinality of eight. The mutation contract removes
each of `projection`, `write`, `category`, and `evidence` in turn and verifies the row cannot return a
result.
