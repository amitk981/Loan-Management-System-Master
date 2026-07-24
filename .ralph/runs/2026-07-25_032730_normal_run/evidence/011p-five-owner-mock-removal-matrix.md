# Epic 011P Five-Owner Mock-Removal Matrix

Command:

```text
rg -n "mockData|from '../../data/mockData'|from '../data/mockData'" \
  sfpcl-lms/src/pages/defaults/DefaultRecoveryHub.tsx \
  sfpcl-lms/src/pages/closure/LoanClosureHub.tsx \
  sfpcl-lms/src/pages/compliance/ComplianceDashboard.tsx \
  sfpcl-lms/src/pages/compliance/GrievancesHub.tsx \
  sfpcl-lms/src/pages/compliance/AuditArchiveHub.tsx
```

Result: no matches.

| Original 011P owner | Final owner slice | Backend-owned state |
|---|---|---|
| `DefaultRecoveryHub.tsx` | 011PA/011PB | Default, notes, decision, recovery projections |
| `LoanClosureHub.tsx` | 011PC | Readiness, closure, NOC, security return, archive projections |
| `ComplianceDashboard.tsx` | 011PD | Controls, tasks, statutory trackers, KYC and reports |
| `GrievancesHub.tsx` | 011PE | Grievance list, projected actions, canonical resolution |
| `AuditArchiveHub.tsx` | 011PE | Searchable retained archive manifests and audited reads |

The two 011PE page tests additionally import each owner as raw source and reject its former mock
identifier/business fixture markers.
