# Aggregate Constraint Matrix

| State | Required | Forbidden |
|---|---|---|
| Pending authorisation | Initiated/manual disbursement and complete initiation relations | Checker/time/comment/role/team/action/evidence/request/network/audit/workflow; non-pending transfer; UTR; disbursed time; advice; register flag |
| Approved | Distinct checker, time, non-empty bounded comment, exact CFC role, team list, action/evidence/request/network/audit/workflow | Same maker/checker or incomplete terminal tuple |
| Rejected | Same complete terminal tuple as approved | Processing/successful transfer, UTR, disbursed time, advice, register flag |
| Later transfer state | Approved authorisation | Pending/rejected authorisation |

The focused direct-ORM tests prove pending transfer/reference/time/register and orphan terminal
facts raise database integrity errors. Existing public approval and rejection tests prove valid
terminal tuples remain writable; migration sync is green.
